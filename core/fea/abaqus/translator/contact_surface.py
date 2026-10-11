from collections import defaultdict
from core.fea.geometry_compute import GeometryCompute


class ContactSurface:
    """Resolve LS-DYNA contact selections into Abaqus element faces.

    Face numbers use the connectivity written by ElementTranslator, including
    its LS-DYNA wedge -> C3D6 node permutation. Internal solid faces are removed.
    """

    connectivity = {
        "s3": (1, 2, 3), "s4": (1, 2, 3, 4),
        "tetra4": (1, 2, 3, 4), "pyramid5": (1, 2, 3, 4, 5),
        "penta6": (1, 5, 2, 4, 7, 3), "hex8": (1, 2, 3, 4, 5, 6, 7, 8),
    }
    solid_faces = {
        "tetra4": ((1, 2, 3), (1, 4, 2), (2, 4, 3), (3, 4, 1)),
        "pyramid5": ((1, 2, 3, 4), (1, 5, 2), (2, 5, 3), (3, 5, 4), (4, 5, 1)),
        "penta6": ((1, 2, 3), (4, 6, 5), (1, 4, 5, 2), (2, 5, 6, 3), (3, 6, 4, 1)),
        "hex8": ((1, 2, 3, 4), (5, 8, 7, 6), (1, 5, 6, 2),
                 (2, 6, 7, 3), (3, 7, 8, 4), (4, 8, 5, 1)),
    }

    def __init__(self, dataframe):
        self.dataframe = dataframe
        # Scoped to this translation, never retained across files/mesh edits.
        self.compute = GeometryCompute()
        self._selections = {}
        self._centers = {}
        self._face_index = None

    def resolve(self, selection_id, selection_type):
        selection_id, selection_type = int(selection_id), int(selection_type)
        key = (selection_id, selection_type)
        if key not in self._selections:
            self._selections[key] = self._resolve(selection_id, selection_type)
        return self._selections[key]

    def _resolve(self, selection_id, selection_type):
        if selection_type == 0:
            return self._segments(selection_id)
        if selection_type == 1:
            selection = self.dataframe.set_shell_list[selection_id]
            elements = [self.dataframe.element_shell[int(uid)] for uid in selection.ids if int(uid)]
        elif selection_type in (2, 3):
            pids = [selection_id] if selection_type == 3 else self.dataframe.set_part_list[selection_id].ids
            elements = []
            for pid in dict.fromkeys(int(pid) for pid in pids if int(pid)):
                if pid not in self.dataframe.part:
                    raise ValueError(f"Missing part {pid} in contact selection {selection_id}")
                part_elements = self.dataframe.storge_part_element.get(pid, [])
                if not part_elements:
                    raise ValueError(f"Part {pid} has no supported contact elements")
                elements.extend(part_elements)
        else:
            raise ValueError(f"Unsupported surface selection type {selection_type} (ID {selection_id})")
        return self._exterior(elements)

    def _element_faces(self, element):
        if element.format not in self.connectivity:
            raise ValueError(f"Unsupported contact element {element.uid}: {element.format}")
        nodes = tuple(getattr(element, f"n{i}") for i in self.connectivity[element.format])
        if element.format in ("s3", "s4"):
            return [(element.uid, None, nodes)]
        return [(element.uid, f"S{index}", tuple(nodes[i - 1] for i in face))
                for index, face in enumerate(self.solid_faces[element.format], 1)]

    def _exterior(self, elements):
        shell_faces, solid_faces = [], defaultdict(list)
        seen = set()
        for element in elements:
            if element.uid in seen:
                continue
            seen.add(element.uid)
            for face in self._element_faces(element):
                if face[1] is None:
                    shell_faces.append(face)
                else:
                    solid_faces[tuple(sorted(face[2]))].append(face)
        if any(len(faces) > 2 for faces in solid_faces.values()):
            raise ValueError("Non-manifold solid mesh in contact selection")
        result = shell_faces + [faces[0] for faces in solid_faces.values() if len(faces) == 1]
        if not result:
            raise ValueError("Contact selection has no exposed faces")
        return result

    def _segments(self, selection_id):
        segments = self.dataframe.set_segment[selection_id].segments
        if self._face_index is None:
            self._face_index = defaultdict(list)
            from itertools import chain
            for element in chain(self.dataframe.element_shell.values(), self.dataframe.element_solid.values()):
                for face in self._element_faces(element):
                    self._face_index[tuple(sorted(set(face[2])))].append(face)
                if element.format in ('s3', 's4'):
                    ns = tuple(getattr(element, f'n{i}') for i in self.connectivity[element.format])
                    for j, (a, b) in enumerate(zip(ns, ns[1:] + ns[:1]), 1):
                        self._face_index[tuple(sorted((a,b)))].append((element.uid, f'E{j}', (a,b)))
        face_index = self._face_index
        result = []
        for segment in segments:
            key = tuple(sorted(set(segment)))
            matches = face_index.get(key, [])
            if not matches or (len(segment) != 2 and len(matches) != 1):
                raise ValueError(f"Segment {segment} must identify exactly one element face")
            result.extend(matches)
        if not result:
            raise ValueError(f"Empty segment set {selection_id}")
        return list(dict.fromkeys(result))

    def orient_shells(self, faces, opposite_faces):
        """Choose the shell side facing the nearest opposing facet centroid.

        This is an initial-geometry conversion of automatic two-sided contact.
        Ambiguous coplanar/overlapping surfaces require explicit user modeling.
        """
        shells = [face for face in faces if face[1] is None]
        if not shells:
            return [(uid, side) for uid, side, _ in faces]
        opposite_centers = [self._center(face[2]) for face in opposite_faces]
        indices = iter(self.compute.nearest([self._center(face[2]) for face in shells], opposite_centers))
        result = []
        for uid, side, nodes in faces:
            if side is None:
                center = self._center(nodes)
                nearest = opposite_centers[next(indices)]
                xyz = [self.dataframe.node[node].xyz for node in nodes]
                # Newell normal is stable for planar triangles and quadrilaterals.
                normal = [0.0, 0.0, 0.0]
                for p, q in zip(xyz, xyz[1:] + xyz[:1]):
                    normal[0] += (p[1] - q[1]) * (p[2] + q[2])
                    normal[1] += (p[2] - q[2]) * (p[0] + q[0])
                    normal[2] += (p[0] - q[0]) * (p[1] + q[1])
                distance = tuple(a - b for a, b in zip(nearest, center))
                dot = sum(a * b for a, b in zip(normal, distance))
                scale = (sum(a * a for a in normal) * sum(a * a for a in distance)) ** 0.5
                if scale == 0 or abs(dot) <= 1e-10 * scale:
                    raise ValueError(f"Cannot determine contact side of shell {uid} from initial geometry")
                side = "SPOS" if dot > 0 else "SNEG"
            result.append((uid, side))
        return result

    def _center(self, nodes):
        nodes = tuple(nodes)
        if nodes in self._centers:
            return self._centers[nodes]
        points = [self.dataframe.node[node].xyz for node in nodes]
        center = tuple(sum(point[i] for point in points) / len(points) for i in range(3))
        self._centers[nodes] = center
        return center

    @staticmethod
    def write_surface(name, faces):
        groups = defaultdict(set)
        for uid, side in faces:
            groups[side].add(uid)
        lines = []
        for side, ids in sorted(groups.items()):
            lines.append(f"*ELSET, ELSET={name}_{side}\n")
            ids = sorted(ids)
            for start in range(0, len(ids), 16):
                lines.append(", ".join(str(uid) for uid in ids[start:start + 16]) + "\n")
        lines.append(f"*SURFACE, NAME={name}, TYPE=ELEMENT\n")
        # Omit the face identifier for double-sided general-contact shells.
        # BOTH is an internal grouping label, not an Abaqus face identifier.
        lines.extend(f"{name}_{side}, {'' if side == 'BOTH' else side}\n" for side in sorted(groups))
        return lines
