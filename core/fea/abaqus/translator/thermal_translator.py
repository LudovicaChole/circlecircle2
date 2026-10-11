"""Uncoupled heat transfer: constant isotropic conduction and prescribed flux/T."""
from collections import defaultdict
from core.fea.conversion_notes import unconverted
from .analysis_data import period, curve_points, node_ids
from .contact_surface import ContactSurface
from utilities.source_location import diagnostic


def thermal_mode(df):
    return next((obj.soln for obj in df.control_solution.values()), 0)


def translate_thermal(df):
    records = list(df.storge['thermal'].values())
    controls = [r for r in records if r.keyword == '*CONTROL_THERMAL_SOLVER']
    if len(controls) != 1 or controls[0].atype not in (0, 1):
        raise ValueError('Thermal conversion requires one steady/transient CONTROL_THERMAL_SOLVER')
    if df.storge['element_beam']:
        raise ValueError('Thermal beam/conduction-link mapping is not implemented')
    for note in df.storge['conversion_notes']:
        if any(k in note for k in ('*BOUNDARY_', '*CONTACT_', '*MAT_THERMAL_', '*LOAD_HEAT_')):
            raise ValueError(f'Thermal analysis has an unmapped boundary/material: {note}')
    control = controls[0]
    # EQHEAT/FWORK apply to mechanical heat production, absent in this route.
    # SBC is unused without radiation, which is rejected by the boundary audit.
    materials = {}
    for record in records:
        if record.keyword == '*MAT_THERMAL_ISOTROPIC':
            if record.tmid in materials:
                raise ValueError(f'Duplicate thermal material {record.tmid}')
            materials[record.tmid] = record
    lines = ['** Uncoupled heat transfer; source consistent units are retained.\n', '*NODE\n']
    lines += [f'{n.uid}, {n.x:.12g}, {n.y:.12g}, {n.z:.12g}\n' for n in df.node.values()]
    shells, faces, element_groups = set(), defaultdict(list), {}
    elements = [*df.element_shell.values(), *df.element_solid.values()]
    if not elements:
        raise ValueError('Thermal source contains no supported elements')
    for element in elements:
        part = df.part[element.pid]
        group = f'thermal_part_{element.pid}'
        connectivity = ContactSurface.connectivity[element.format]
        nodes = [getattr(element, f'n{i}') for i in connectivity]
        if element.format in ('s3', 's4'):
            section = df.section_shell[part.secid]
            if section.elform in (12, 13, 14, 15):
                kind = ('DCAX' if section.elform in (14, 15) else 'DC2D') + str(len(nodes))
                if any(df.node[n].z != 0 for n in nodes):
                    raise ValueError('Planar/axisymmetric thermal mesh must lie in the XY plane')
                for i, nid in enumerate(nodes):
                    faces[frozenset((nid, nodes[(i+1) % len(nodes)]))].append((element.uid, f'S{i+1}'))
            else:
                kind = 'DS' + str(len(nodes))
                shells.update(nodes)
                faces[frozenset(nodes)].append((element.uid, None))
        else:
            if element.format == 'pyramid5':
                raise ValueError('Five-node thermal pyramid mapping is not implemented')
            kind = 'DC3D' + str(len(nodes))
            for i, face in enumerate(ContactSurface.solid_faces[element.format], 1):
                faces[frozenset(nodes[j-1] for j in face)].append((element.uid, f'S{i}'))
        element_groups.setdefault((group, kind), []).append(f'{element.uid}, ' + ', '.join(map(str, nodes)) + '\n')
    for (group, kind), rows in element_groups.items():
        lines += [f'*ELEMENT, TYPE={kind}, ELSET={group}\n', *rows]
    body_flux = []
    for pid in dict.fromkeys(e.pid for e in elements):
        part = df.part[pid]
        if part.tmid not in materials:
            raise ValueError(diagnostic(f'PART {pid}: missing thermal material TMID={part.tmid}', part))
        mat = materials[part.tmid]
        if mat.tlat or mat.hlat or mat.tgrlc:
            raise ValueError(diagnostic('Temperature/curve-dependent heat generation or latent heat is not mapped', mat))
        density = mat.tro or getattr(df.material.get(part.mid), 'ro', 0)
        if mat.tc <= 0 or (control.atype and (density <= 0 or mat.hc <= 0)):
            raise ValueError(diagnostic('Thermal conductivity and transient density/specific heat must be positive', mat))
        name, group = f'thermal_material_part_{pid}', f'thermal_part_{pid}'
        lines += [f'*MATERIAL, NAME={name}\n', '*CONDUCTIVITY\n', f'{mat.tc:.12g}\n']
        if density > 0:
            lines += ['*DENSITY\n', f'{density:.12g}\n']
        if mat.hc > 0:
            lines += ['*SPECIFIC HEAT\n', f'{mat.hc:.12g}\n']
        section = df.section_shell.get(part.secid)
        if section and section.elform not in (12, 13, 14, 15):
            if len({section.t1, section.t2, section.t3, section.t4}) != 1 or section.t1 <= 0:
                raise ValueError('Thermal shell requires positive uniform thickness')
            lines += [f'*SHELL SECTION, ELSET={group}, MATERIAL={name}\n', f'{section.t1:.12g}, 3\n']
        else:
            lines += [f'*SOLID SECTION, ELSET={group}, MATERIAL={name}\n',
                      f'{section.t1:.12g}\n' if section and section.elform in (12, 13) else '\n']
        if mat.tgmult:
            body_flux += [f'{group}, BF, {mat.tgmult:.12g}\n']
    amplitudes, boundary, fluxes = [], [], []
    end = period(df, 1.0)

    def amplitude(lcid, uid):
        if lcid < 0:
            raise ValueError('Temperature-dependent boundary curve requires a user subroutine')
        if not lcid:
            return ''
        points = curve_points(df.define_curve[lcid])
        name = f'thermal_curve_{uid}'
        amplitudes.append(f'*AMPLITUDE, NAME={name}, TIME=TOTAL TIME\n')
        amplitudes.extend(f'{x:.12g}, {y:.12g}\n' for x, y in points)
        return f', AMPLITUDE={name}'

    for uid, record in enumerate(records, 1):
        try:
            keyword = record.keyword
            if keyword.startswith(('*INITIAL_TEMPERATURE', '*BOUNDARY_TEMPERATURE')):
                selected = (list(df.node) if record.target == 0 else df.set_node_list[record.target].ids
                            ) if keyword.endswith('_SET') else [record.target]
                selected = node_ids(df, selected)
                if record.loc not in (-1, 0, 1):
                    raise ValueError('Temperature LOC must be -1, 0 or 1')
                if keyword.startswith('*INITIAL'):
                    if record.loc:
                        raise ValueError('Initial shell temperature gradients are not mapped')
                    lines += ['*INITIAL CONDITIONS, TYPE=TEMPERATURE\n']
                    lines += [f'{nid}, {record.temp:.12g}\n' for nid in sorted(selected)]
                else:
                    if record.tbirth or record.tdeath < end:
                        raise ValueError('Temperature BIRTH/DEATH requires multiple analysis steps')
                    boundary += [f'*BOUNDARY{amplitude(record.tlcid, uid)}\n']
                    for nid in sorted(selected):
                        if nid not in shells and record.loc:
                            raise ValueError('Nonzero temperature LOC requires shell nodes')
                        dof = 12 + record.loc if nid in shells else 11
                        boundary.append(f'{nid}, {dof}, {dof}, {record.tmult:.12g}\n')
            elif keyword.startswith('*BOUNDARY_CONVECTION'):
                if getattr(record, 'pserod', 0) or record.hmult < 0:
                    raise ValueError('Convection requires nonnegative coefficient and no eroding face set')
                films = amplitude(record.hlcid, f'{uid}_h').replace('AMPLITUDE=', 'FILM AMPLITUDE=')
                sinks = amplitude(record.tlcid, f'{uid}_t').replace('AMPLITUDE=', 'SINK AMPLITUDE=')
                fluxes.append(f'*FILM{films}{sinks}\n')
                segments = df.set_segment[record.ssid].segments if keyword.endswith('_SET') else [
                    (record.n1, record.n2, record.n3, record.n4)]
                for segment in segments:
                    matches = faces.get(frozenset(n for n in segment if n), [])
                    if len(matches) != 1:
                        raise ValueError(f'Convection segment {segment} must identify exactly one exterior face')
                    eid, face = matches[0]
                    if face is None:
                        if record.loc not in (-1, 1):
                            raise ValueError('Thermal shell middle-surface convection is not mapped')
                        face = 'SNEG' if record.loc == -1 else 'SPOS'
                    fluxes.append(f'{eid}, F{face[1:]}, {record.tmult:.12g}, {record.hmult:.12g}\n')
            elif keyword.startswith('*BOUNDARY_FLUX'):
                if record.nhisv or getattr(record, 'pserod', 0):
                    raise ValueError('Flux history variables/erosion are not mapped')
                scales = (record.mlc1, record.mlc2, record.mlc3, record.mlc4)
                if len(set(scales)) != 1:
                    raise ValueError('Spatially varying segment flux requires a user subroutine')
                segments = df.set_segment[record.ssid].segments if keyword.endswith('_SET') else [
                    (record.n1, record.n2, record.n3, record.n4)]
                fluxes.append(f'*DFLUX{amplitude(record.lcid, uid)}\n')
                for segment in segments:
                    matches = faces.get(frozenset(n for n in segment if n), [])
                    if len(matches) != 1:
                        raise ValueError(f'Flux segment {segment} must identify exactly one exterior face')
                    eid, face = matches[0]
                    if face is None:
                        if record.loc not in (-1, 1):
                            raise ValueError('Thermal shell middle-surface flux is not mapped')
                        face = 'SNEG' if record.loc == -1 else 'SPOS'
                    fluxes.append(f'{eid}, {face}, {-scales[0]:.12g}\n')
        except (KeyError, ValueError) as error:
            raise ValueError(diagnostic(str(error), record)) from error
    timestep = next((r for r in records if r.keyword == '*CONTROL_THERMAL_TIMESTEP'), None)
    increment = min(end, timestep.its) if timestep and timestep.its > 0 else end
    if timestep and (timestep.lcts or timestep.tip != 1 or min(timestep.tmin, timestep.tmax, timestep.dtemp) < 0):
        raise ValueError(diagnostic('Thermal curve-based time steps/Crank-Nicolson are not mapped', timestep))
    mode = ', STEADY STATE' if control.atype == 0 else (
        f', DELTMX={timestep.dtemp or 1:.12g}' if timestep and timestep.ts == 1 else '')
    step = amplitudes + ['*STEP, NAME=HeatTransfer, INC=100000, AMPLITUDE=STEP\n', f'*HEAT TRANSFER{mode}\n',
        f'{increment:.12g}, {end:.12g}\n', *boundary, *fluxes]
    if body_flux:
        step += ['*DFLUX\n', *body_flux]
    step += ['*OUTPUT, FIELD\n', '*NODE OUTPUT\n', 'NT, RFL\n', '*ELEMENT OUTPUT\n', 'HFL\n', '*END STEP\n']
    df.output_storge['*THERMAL_MODEL'] = lines
    df.output_storge['*THERMAL_STEP'] = step
    unconverted('Thermal numerical solver controls replaced by Abaqus heat-transfer solver defaults', control)
