"""Read a single, meshed Abaqus towing template and preserve its solid materials.

Ambiguous assemblies, CAD-only GEO, higher-order elements, and unsupported
section/material dependencies are rejected rather than silently discarded.
"""
import numpy as np
from core.fea.dataframe import DataFrame
from core.fea.abaqus.parser.input_reader import blocks, options
from core.fea.abaqus.parser.node_parser import NodeParser
from core.fea.abaqus.parser.element_parser import ElementParser
from core.fea.abaqus.parser.elset_parser import ElsetParser, resolve
from core.fea.mesh_data import rebuild_indices
from core.hmdesktop.towing_geometry import exterior, fit_cylinder, cylindrical_faces
from core.fea.abaqus.translator.contact_surface import ContactSurface


def read_template(path):
    df, sets, sections, materials = DataFrame(), {}, [], {}
    parser = NodeParser()
    parser.dataframe = df
    current_material = None
    part_count = 0
    allowed_material = {'*DENSITY', '*ELASTIC', '*PLASTIC', '*EXPANSION', '*DAMPING'}
    for location, header, rows in blocks(path):
        key, opts = options(header)
        if key == '*PART':
            part_count += 1
            if part_count > 1:
                raise ValueError('Towing template must contain one mesh part; export the desired part alone.')
        elif key in ('*ASSEMBLY', '*INSTANCE'):
            raise ValueError('Export the towing template as a single mesh without assembly instances.')
        elif key == '*NODE':
            if set(opts)-{'NSET'}:
                raise ValueError('Towing template nodes must use global Cartesian coordinates.')
            for row in rows:
                parser.parse(row, '2024')
        elif key == '*ELEMENT':
            if opts.get('TYPE', '').upper() not in ('C3D6', 'C3D8', 'C3D8R', 'C3D8I'):
                raise ValueError('Towing templates require C3D6 or C3D8-family solids; tetrahedra are excluded.')
            before = set(df.element_solid)
            ElementParser().parse(opts, rows, df, sets)
            for eid in df.element_solid.keys()-before:
                df.element_solid[eid].abaqus_type = opts['TYPE'].upper()
        elif key == '*ELSET':
            ElsetParser().parse(opts, rows, sets)
        elif key == '*SOLID SECTION':
            if set(opts)-{'ELSET', 'MATERIAL'} or any(row.strip(', ') for row in rows):
                raise ValueError('Towing template supports homogeneous solid sections without extra dependencies.')
            sections.append((opts['ELSET'].upper(), opts['MATERIAL'].upper()))
        elif key == '*MATERIAL':
            current_material = opts['NAME'].upper()
            materials[current_material] = []
        elif key in allowed_material and current_material:
            if 'DEPENDENCIES' in opts or 'DISTRIBUTION' in opts:
                raise ValueError('Template material dependencies need explicit modeling.')
            if key == '*ELASTIC' and opts.get('TYPE', 'ISOTROPIC').upper() != 'ISOTROPIC':
                raise ValueError('Template anisotropic materials require orientation-aware transformation.')
            materials[current_material].extend([header+'\n', *(row+'\n' for row in rows)])
        elif key in ('*HEADING', '*END PART', '*NSET'):
            current_material = None
        else:
            raise ValueError(f'{location}: unsupported towing template keyword {key}; export mesh and materials only.')
    rebuild_indices(df)
    if not df.element_solid or not sections:
        raise ValueError('Template has no solid mesh/sections. GEO must be an Abaqus mesh, not CAD geometry.')
    assigned = set()
    for name, material in sections:
        if material not in materials or not materials[material]:
            raise ValueError(f'Template section {name}: material {material} missing or empty.')
        ids = set(resolve(sets, name))
        if not ids <= df.element_solid.keys() or assigned & ids:
            raise ValueError('Template sections contain missing or multiply assigned elements.')
        assigned.update(ids)
    if assigned != set(df.element_solid):
        raise ValueError('Every template solid element needs a material section.')
    return df, sets, sections, materials


def copy_template(template, hole, length, first_node, first_element, name, predictor):
    df, sets, sections, materials = template
    ids = sorted(df.node)
    points = np.array([df.node[n].xyz for n in ids])
    probability = predictor.probability(points)
    if probability < predictor.threshold:
        raise ValueError(f'Towing NN did not recognize the template (confidence {probability:.3f}).')
    source = fit_cylinder(df, 0, hollow=False)
    if abs(source.radius-hole.radius) > max(hole.radius*.03, hole.tolerance):
        raise ValueError(f'Template radius {source.radius:g} does not match hole radius {hole.radius:g}; shape is not rescaled.')
    # Preserve the entire shape and material. L selects the end/direction only.
    sign = 1 if length > 0 else -1
    anchor = hole.low if sign > 0 else hole.high
    source_anchor = source.low if sign > 0 else source.high
    source_frame = np.column_stack((source.u, source.v, source.axis))
    target_frame = np.column_stack((hole.u, hole.v, hole.axis))
    local = (points-source.center) @ source_frame
    local[:, 2] -= source_anchor
    moved = local @ target_frame.T+hole.center+anchor*hole.axis
    node_map = {old: first_node+i for i, old in enumerate(ids)}
    elements = sorted(df.element_solid.values(), key=lambda element: element.uid)
    element_map = {element.uid: first_element+i for i, element in enumerate(elements)}
    lines = [f'** Towing template {name}; original shape and length preserved\n', '*NODE\n']
    lines.extend(f'{node_map[old]}, {xyz[0]:.12g}, {xyz[1]:.12g}, {xyz[2]:.12g}\n' for old, xyz in zip(ids, moved))
    for kind in ('C3D6', 'C3D8', 'C3D8R', 'C3D8I'):
        group = [e for e in elements if e.abaqus_type == kind]
        if group:
            lines.append(f'*ELEMENT, TYPE={kind}\n')
            for element in group:
                conn = [node_map[getattr(element, f'n{i}')] for i in ContactSurface.connectivity[element.format]]
                lines.append(f'{element_map[element.uid]}, '+', '.join(map(str,conn))+'\n')
    for index, (elset, material) in enumerate(sections):
        section_name, mat_name = f'{name}_SEC{index}', f'{name}_MAT{index}'
        lines.append(f'*ELSET, ELSET={section_name}\n')
        assigned = [element_map[eid] for eid in resolve(sets,elset)]
        lines.extend(', '.join(map(str,assigned[i:i+16]))+'\n' for i in range(0,len(assigned),16))
        lines.extend([f'*MATERIAL, NAME={mat_name}\n', *materials[material],
                      f'*SOLID SECTION, ELSET={section_name}, MATERIAL={mat_name}\n', ',\n'])
    # Transform a private copy of the mesh before selecting only overlapping wall faces.
    for old, xyz in zip(ids, moved):
        node = df.node[old]
        node.x, node.y, node.z = map(float, xyz)
        node.xyz = tuple(map(float, xyz))
    low = max(hole.low, anchor if sign > 0 else anchor-(source.high-source.low))
    high = min(hole.high, anchor+(source.high-source.low) if sign > 0 else anchor)
    faces = cylindrical_faces(df, exterior(df,0), hole, low, high)
    if not faces:
        raise ValueError('No template cylindrical faces overlap the hole.')
    return lines, [(element_map[eid], side) for eid, side in faces], first_node+len(ids), first_element+len(elements), low, high
