"""Mesh cylinder fitting and non-tetrahedral Abaqus towing insert construction.

Recognition is performed by core.nn; this module only verifies and assembles geometry.
"""
from dataclasses import dataclass
from collections import defaultdict
import math
import numpy as np
from core.fea.abaqus.translator.contact_surface import ContactSurface


@dataclass
class Cylinder:
    center: np.ndarray
    axis: np.ndarray
    u: np.ndarray
    v: np.ndarray
    radius: float
    low: float
    high: float
    tolerance: float

    def coordinates(self, points):
        delta = np.asarray(points) - self.center
        axial = delta @ self.axis
        radial = np.sqrt((delta @ self.u)**2 + (delta @ self.v)**2)
        return axial, radial


def basis(axis):
    axis = np.asarray(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    if axis[np.argmax(np.abs(axis))] < 0:
        axis = -axis
    reference = np.eye(3)[np.argmin(np.abs(axis))]
    u = np.cross(reference, axis)
    u /= np.linalg.norm(u)
    return axis, u, np.cross(axis, u)


def exterior(df, pid):
    return ContactSurface(df)._exterior(df.storge_part_element[pid])


def refine_cylinder(cylinder, points):
    """Refine axis and radius together using robust local least squares."""
    base = cylinder
    parameters = np.array([0., 0., 0., 0., base.radius])
    def residual(values):
        cx, cy, tx, ty, radius = values
        axis = base.axis+tx*base.u+ty*base.v
        axis /= np.linalg.norm(axis)
        center = base.center+cx*base.u+cy*base.v
        delta = points-center
        radial_squared = np.maximum((delta*delta).sum(axis=1)-(delta@axis)**2, 0)
        return np.sqrt(radial_squared)-radius
    for _ in range(25):
        values = residual(parameters)
        mask = abs(values) < max(base.radius*.06, base.tolerance)
        if mask.sum() < 12:
            break
        step_sizes = [base.radius*1e-5, base.radius*1e-5, 1e-5, 1e-5, base.radius*1e-5]
        columns = []
        for index, step in enumerate(step_sizes):
            shifted = parameters.copy()
            shifted[index] += step
            columns.append((residual(shifted)[mask]-values[mask])/step)
        matrix = np.column_stack(columns)
        weights = np.sqrt(np.minimum(1., base.radius*.002/np.maximum(abs(values[mask]),1e-12)))
        delta = np.linalg.lstsq(matrix*weights[:,None], -values[mask]*weights, rcond=None)[0]
        if not np.isfinite(delta).all() or np.linalg.norm(delta[2:4]) > .15:
            break
        parameters += delta
        if np.linalg.norm(delta) < 1e-8:
            break
    cx, cy, tx, ty, radius = parameters
    axis, u, v = basis(base.axis+tx*base.u+ty*base.v)
    result = Cylinder(base.center+cx*base.u+cy*base.v, axis,u,v,float(radius),0,0,base.tolerance)
    axial, radial = result.coordinates(points)
    selected = abs(radial-radius) < result.tolerance
    if radius <= 0 or selected.sum() < 12:
        return base
    result.low, result.high = float(axial[selected].min()), float(axial[selected].max())
    return result


def facing_wall(df, faces, cylinder, hollow):
    """Distinguish a solid bore from an outer wall using element-interior direction."""
    result = []
    for eid, side in faces:
        element = df.element_solid.get(eid)
        if element is None:
            result.append((eid,side))
            continue
        all_nodes = [getattr(element,f'n{i}') for i in ContactSurface.connectivity[element.format]]
        face_indices = ContactSurface.solid_faces[element.format][int(side[1:])-1]
        face_center = np.mean([df.node[all_nodes[i-1]].xyz for i in face_indices],axis=0)
        interior = np.mean([df.node[n].xyz for n in all_nodes],axis=0)
        radial = face_center-cylinder.center
        radial -= cylinder.axis*(radial@cylinder.axis)
        outward = face_center-interior
        dot = outward@radial
        if (hollow and dot < -1e-9) or (not hollow and dot > 1e-9):
            result.append((eid,side))
    return result


def fit_cylinder(df, pid, hollow=True):
    ids = sorted(df.storge_part_node_id[pid])
    points = np.array([df.node[n].xyz for n in ids])
    origin = points.mean(axis=0)
    _, _, vectors = np.linalg.svd(points-origin, full_matrices=False)
    axes = [*np.eye(3), *vectors]
    faces = exterior(df, pid)
    normals = []
    for _, _, nodes in faces:
        xyz = np.array([df.node[n].xyz for n in nodes])
        normal = np.cross(xyz[1]-xyz[0], xyz[2]-xyz[0])
        length = np.linalg.norm(normal)
        if length > 1e-10:
            normals.append(normal/length)
    if normals:
        normals = np.array(normals)
        _, _, normal_vectors = np.linalg.svd(normals, full_matrices=False)
        axes.extend(normal_vectors)
        rng = np.random.default_rng(71)
        for _ in range(40):
            a, b = normals[rng.integers(len(normals), size=2)]
            cross = np.cross(a, b)
            if np.linalg.norm(cross) > .2:
                axes.append(cross/np.linalg.norm(cross))
    unique = []
    for axis in axes:
        axis, _, _ = basis(axis)
        if not any(abs(axis @ old) > 1-1e-9 for old in unique):
            unique.append(axis)
    candidates = []
    rng = np.random.default_rng(72)
    sample = points if len(points) <= 1600 else points[rng.choice(len(points), 1600, replace=False)]
    for candidate_axis in unique:
        axis, u, v = basis(candidate_axis)
        xy = np.column_stack(((sample-origin) @ u, (sample-origin) @ v))
        trials = [np.arange(len(xy))]
        trials.extend(rng.choice(len(xy), 3, replace=False) for _ in range(80))
        best = []
        for indices in trials:
            subset = xy[indices]
            matrix = np.column_stack((2*subset, np.ones(len(subset))))
            if np.linalg.matrix_rank(matrix) < 3:
                continue
            cx, cy, constant = np.linalg.lstsq(matrix, (subset**2).sum(axis=1), rcond=None)[0]
            squared = constant+cx*cx+cy*cy
            if squared <= 1e-12:
                continue
            radius = math.sqrt(squared)
            # Do not accept circles vastly larger than the mesh (nearly straight lines).
            if radius > np.linalg.norm(np.ptp(sample, axis=0)):
                continue
            tolerance = max(radius*.025, 1e-6)
            distance = np.linalg.norm(xy-[cx, cy], axis=1)
            mask = abs(distance-radius) <= tolerance
            if mask.sum() < max(12, len(sample)*.08):
                continue
            angle = np.arctan2(xy[mask,1]-cy, xy[mask,0]-cx)
            bins = np.unique(((angle+np.pi)*12/(2*np.pi)).astype(int) % 12)
            if len(bins) < 10:
                continue
            center = origin+cx*u+cy*v
            cylinder = Cylinder(center, axis, u, v, radius, 0, 0, tolerance)
            axial, radial = cylinder.coordinates(points)
            selected = abs(radial-radius) <= tolerance
            low, high = axial[selected].min(), axial[selected].max()
            if high-low < radius*.15:
                continue
            cylinder.low, cylinder.high = float(low), float(high)
            wall_faces = facing_wall(df,cylindrical_faces(df, faces, cylinder, low, high),cylinder,hollow)
            if len(wall_faces) < 8:
                continue
            best.append((len(wall_faces), cylinder))
        if best:
            best.sort(key=lambda item: item[0], reverse=True)
            # Comparable concentric surfaces: hollow meshes use the inner radius.
            largest = best[0][0]
            eligible = [item for item in best if item[0] >= largest*.65]
            selected = min(eligible, key=lambda item: item[1].radius) if hollow else max(eligible, key=lambda item: item[1].radius)
            candidates.append(selected)
    if not candidates:
        raise ValueError(f'Part {pid}: no well-supported cylindrical wall could be fitted.')
    refined = []
    for _, candidate in candidates:
        candidate = refine_cylinder(candidate,points)
        count = len(facing_wall(df,cylindrical_faces(df,faces,candidate,candidate.low,candidate.high),candidate,hollow))
        refined.append((count,candidate))
    refined.sort(key=lambda item: item[0], reverse=True)
    if refined[0][0] < 8:
        raise ValueError(f'Part {pid}: fitted cylinder has insufficient wall support.')
    return refined[0][1]


def cylindrical_faces(df, faces, cylinder, low, high):
    result = []
    for eid, side, nodes in faces:
        xyz = np.array([df.node[n].xyz for n in nodes])
        axial, radial = cylinder.coordinates(xyz)
        if np.max(abs(radial-cylinder.radius)) > cylinder.tolerance:
            continue
        if np.ptp(axial) < cylinder.tolerance*.1:
            continue  # End caps are not the cylindrical overlap surface.
        if axial.min() < low-cylinder.tolerance or axial.max() > high+cylinder.tolerance:
            continue
        if side is None:
            normal = np.cross(xyz[1]-xyz[0], xyz[2]-xyz[0])
            center = xyz.mean(axis=0)
            delta = center-cylinder.center
            inward = -delta+cylinder.axis*(delta @ cylinder.axis)
            side = 'SPOS' if normal @ inward > 0 else 'SNEG'
        result.append((eid, side))
    return result


def make_insert(cylinder, length, first_node, first_element, name, material_name):
    length = float(length)
    if not math.isfinite(length) or length == 0:
        raise ValueError('Towing L must be finite and nonzero.')
    # Keep the original hole fixed. +L aligns lower caps, -L aligns upper caps.
    low = cylinder.low if length > 0 else cylinder.high-abs(length)
    high = low+abs(length)
    overlap_low, overlap_high = max(low, cylinder.low), min(high, cylinder.high)
    if overlap_high-overlap_low <= cylinder.tolerance:
        raise ValueError('Towing insert has no usable axial overlap.')
    levels = sorted(set([low, high, overlap_low, overlap_high]))
    refined = [levels[0]]
    for a, b in zip(levels, levels[1:]):
        count = max(1, math.ceil((b-a)/max(cylinder.radius, .001)))
        if count > 10000:
            raise ValueError('Towing L would create too many elements.')
        refined.extend(np.linspace(a,b,count+1)[1:])
    sectors = 32
    nodes, elements, surfaces = {}, [], []
    nid, eid = first_node, first_element
    rings = []
    for axial in refined:
        center = cylinder.center+cylinder.axis*axial
        ring = [nid]
        nodes[nid] = center
        nid += 1
        for angle in np.arange(sectors)*2*np.pi/sectors:
            nodes[nid] = center+cylinder.radius*(np.cos(angle)*cylinder.u+np.sin(angle)*cylinder.v)
            ring.append(nid)
            nid += 1
        rings.append(ring)
    for layer, (lower, upper) in enumerate(zip(rings, rings[1:])):
        for sector in range(sectors):
            a, b = sector+1, (sector+1)%sectors+1
            elements.append((eid, (lower[0], lower[a], lower[b], upper[0], upper[a], upper[b])))
            if refined[layer] >= overlap_low-1e-8 and refined[layer+1] <= overlap_high+1e-8:
                surfaces.append((eid, 'S4'))
            eid += 1
    lines = [f'** Towing insert {name}; signed L={length:g}\n', '*NODE\n']
    lines.extend(f'{uid}, {xyz[0]:.12g}, {xyz[1]:.12g}, {xyz[2]:.12g}\n' for uid, xyz in nodes.items())
    lines.append(f'*ELEMENT, TYPE=C3D6, ELSET={name}\n')
    lines.extend(f'{uid}, '+', '.join(map(str, conn))+'\n' for uid, conn in elements)
    lines.extend([f'*SOLID SECTION, ELSET={name}, MATERIAL={material_name}\n', ',\n'])
    return lines, surfaces, nid, eid, overlap_low, overlap_high
