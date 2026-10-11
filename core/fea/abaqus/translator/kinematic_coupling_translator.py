from core.fea.translator import Translator
from utilities.logger import logger


class KinematicCouplingTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.version = {"6.14": self._6p14, "2024": self._6p14}

    def translate(self, version):
        try:
            if version in self.version:
                self.version[version]()
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"ABAQUS KinematicCouplingTranslator ERROR: {e}") from e

    def _node_ids(self, values):
        ids = []
        for value in values:
            raw = str(value).strip()
            nid = int(self.dataframe.parameter[raw[1:]].value) if raw.startswith("&") else int(raw)
            if not nid:
                continue
            if nid not in self.dataframe.node:
                raise ValueError(f"Missing coupling node {nid}")
            ids.append(nid)
        return list(dict.fromkeys(ids))

    def _6p14(self):
        # Validate the complete graph before writing any constraints.
        couplings, reference_nodes, constraints, part_references = {}, {}, {}, {}
        max_node_id = max(self.dataframe.node, default=0)
        for pid, part in self.dataframe.part.items():
            material = self.dataframe.material[part.mid]
            if material.tag != "rigid":
                continue
            nodes = self._node_ids(self.dataframe.storge_part_node_id.get(pid, []))
            if not nodes:
                raise ValueError(f"Rigid part {pid} has no nodes")
            # Preserve the existing geometric-center convention. Extra nodes
            # do not move the original rigid-body reference point.
            points = {self.dataframe.node[nid].xyz for nid in nodes}
            center = tuple(sum(point[i] for point in points) / len(points) for i in range(3))
            max_node_id += 1
            reference_nodes[max_node_id] = center
            constraints[max_node_id] = (material.con1, material.con2)
            part_references[pid] = max_node_id
            couplings[max_node_id] = set(nodes)

        self._add_extra_nodes(couplings, part_references)
        self._validate_ownership(couplings)
        self._add_nodal_rigid_bodies(couplings)
        self._validate_ownership(couplings)

        node_lines, coupling_lines = [], []
        for reference, (x, y, z) in reference_nodes.items():
            node_lines.append(f"{reference:<10},{x:17.10f},{y:17.10f},{z:17.10f}\n")
        for reference, nodes in couplings.items():
            if not nodes:
                continue
            name = f'dyna_rigid_{reference}'
            coupling_lines.append(f'*NSET, NSET={name}\n')
            ids = sorted(nodes)
            for start in range(0, len(ids), 16):
                coupling_lines.append(', '.join(map(str, ids[start:start+16])) + '\n')
            coupling_lines.extend([f'*SURFACE, TYPE=NODE, NAME={name}_surface\n',
                f'{name}, 1.0\n',
                f'*COUPLING, CONSTRAINT NAME={name}_coupling, REF NODE={reference}, SURFACE={name}_surface\n',
                '*KINEMATIC\n', '1, 6\n'])
        if node_lines:
            self.dataframe.output_storge.setdefault("*NODE", []).extend(["*NODE\n"] + node_lines)
        if coupling_lines:
            self.dataframe.output_storge.setdefault("*KINEMATIC", []).extend(coupling_lines)
        self.dataframe.storge_rigid_part_goc_xyz.update(reference_nodes)
        self.dataframe.storge_rigid_part_goc_con.update(constraints)
        self.dataframe.storge_rigid_part_reference_node.update(part_references)

    def _add_extra_nodes(self, couplings, part_references):
        for extra in self.dataframe.constrained_extra_nodes_set.values():
            pid, nsid = int(extra.pid), int(extra.nsid)
            if pid not in part_references:
                raise ValueError(f"Extra node set {nsid} targets part {pid}, which has no MAT20 rigid reference node")
            if nsid not in self.dataframe.set_node_list:
                raise ValueError(f"Part {pid}: missing extra node set {nsid}")
            nodes = self._node_ids(self.dataframe.set_node_list[nsid].ids)
            if not nodes:
                raise ValueError(f"Part {pid}: extra node set {nsid} is empty")
            if extra.iflag:
                logger.warning(f"Part {pid}: extra-node IFLAG={extra.iflag}; coupling is converted, "
                               "but PART_INERTIA mass/inertia updates are not implemented", source=extra)
            couplings[part_references[pid]].update(nodes)

    def _add_nodal_rigid_bodies(self, couplings):
        for body in self.dataframe.constrained_nodal_rigid_body.values():
            nodes = self._node_ids(self.dataframe.set_node_list[body.sid].ids)
            if not nodes:
                raise ValueError(f"Nodal rigid body {body.uid} has an empty node set")
            reference = self._node_ids([body.pnode])[0] if body.pnode else nodes[0]
            # An entire nodal rigid body may already be attached through an
            # EXTRA_NODES_SET. Its relative rigidity is then already enforced.
            # Do not constrain its nodes a second time to a dependent reference.
            if any(set(nodes + [reference]) <= members | {master}
                   for master, members in couplings.items()):
                logger.info(f"Nodal rigid body {body.uid} is already covered by an existing rigid coupling")
                continue
            merged = False
            for master, members in couplings.items():
                shared = set(nodes) & members
                if self._fixes_rigid_motion(shared):
                    # Three non-collinear shared nodes fix the relative rigid
                    # motion. Flatten this redundant rigid-body connection.
                    members.update(set(nodes + [reference]) - {master})
                    logger.info(f"Nodal rigid body {body.uid} merged into reference node {master}")
                    merged = True
                    break
            if merged:
                continue
            couplings.setdefault(reference, set()).update(set(nodes) - {reference})

    def _fixes_rigid_motion(self, nodes):
        if len(nodes) < 3:
            return False
        points = [self.dataframe.node[nid].xyz for nid in sorted(nodes)]
        vectors = [tuple(b - a for a, b in zip(points[0], point)) for point in points[1:]]
        first = max(vectors, key=lambda v: sum(x * x for x in v))
        for second in vectors:
            cross = (first[1] * second[2] - first[2] * second[1],
                     first[2] * second[0] - first[0] * second[2],
                     first[0] * second[1] - first[1] * second[0])
            scale = sum(x * x for x in first) * sum(x * x for x in second)
            if sum(x * x for x in cross) > 1e-20 * scale:
                return True
        return False

    @staticmethod
    def _validate_ownership(couplings):
        owners = {}
        for reference, nodes in couplings.items():
            for nid in nodes:
                if nid in couplings:
                    raise ValueError(f"Reference node {nid} is also a dependent node of {reference}")
                if nid in owners and owners[nid] != reference:
                    raise ValueError(f"Node {nid} is coupled to different reference nodes: {owners[nid]}, {reference}")
                owners[nid] = reference
