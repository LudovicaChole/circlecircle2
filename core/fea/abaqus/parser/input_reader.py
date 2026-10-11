from core.fea.include_reader import load_deck
"""Block orchestration; keyword semantics live in individual parsers."""
from pathlib import Path
import csv
from core.fea.dataframe import dataframe as df
from core.fea.material_cards import register_materials
from core.fea.mesh_data import rebuild_indices
from core.fea.validation import FeaInputError
from utilities.source_location import source_scope, source_location
from utilities.logger import logger
from core.fea.conversion_notes import unconverted
from core.fea.model.lsdyna.part import Part
from core.fea.model.lsdyna.set_node_list import SetNodeList
from .node_parser import NodeParser
from .element_parser import ElementParser
from .elset_parser import ElsetParser, resolve
from .nset_parser import NsetParser
from .shell_section_parser import ShellSectionParser
from .solid_section_parser import SolidSectionParser
from .boundary_parser import BoundaryParser
from .initial_conditions_parser import InitialConditionsParser


def blocks(path, deck=None):
    result, header, rows, start = [], None, [], 0
    continued = False
    deck = deck or load_deck(path, "abaqus")
    for record in deck.lines:
        line = record.text
        line = line.strip()
        if not line or line.startswith('**'):
            continue
        if continued:
            header += line
            continued = header.endswith(',')
        elif line.startswith('*'):
            if header is not None:
                result.append((start, header, rows))
            header, rows, start = line, [], record.location
            continued = line.endswith(',')
        elif header is not None:
            rows.append(line)
    if continued:
        raise FeaInputError(f'{path}: incomplete keyword continuation')
    if header is not None:
        result.append((start, header, rows))
    return result


def options(header):
    fields = next(csv.reader([header], skipinitialspace=True))
    opts = {}
    for field in fields[1:]:
        key, _, val = field.partition('=')
        opts[key.strip().upper()] = val.strip().strip('"')
    return fields[0].upper(), opts


def parse_file(path, version):
    deck = load_deck(path, "abaqus")
    content = blocks(path, deck)
    source_metadata = restore_metadata(deck)
    # The material reader joins continuations while preserving source positions.
    material_text, material_sources = deck.material_input('abaqus')
    register_materials(material_text, 'abaqus', file_path=path, source_map=material_sources)
    elements, nodes, sections, conditions = {}, {}, [], []
    amplitudes, node_surfaces, couplings, masses = {}, {}, [], []
    coupling = None
    for location, header, rows in content:
        keyword, opts = options(header)
        if keyword == '*AMPLITUDE':
            if opts.get('DEFINITION','TABULAR').upper() != 'TABULAR' or set(opts)-{'NAME','TIME','DEFINITION'}:
                raise FeaInputError(f'{location}: only tabular amplitude is supported')
            values = [float(v.strip()) for row in rows for v in row.split(',') if v.strip()]
            if len(values)%2:
                raise FeaInputError(f'{location}: incomplete amplitude pair')
            amplitudes[opts['NAME'].upper()] = list(zip(values[::2],values[1::2]))
    in_step = False
    materials = {m.name.upper(): mid for mid,m in df.material.items()}
    for line, header, rows in content:
        keyword, opts = options(header)
        location = f'{line}: {keyword}'
        try:
            with source_scope(location):
                if keyword == '*STEP':
                    in_step = True
                elif keyword == '*END STEP':
                    in_step = False
                if keyword in ('*PART', '*INSTANCE', '*ASSEMBLY', '*SYSTEM', '*TRANSFORM'):
                    raise ValueError(f'{keyword}: flatten instances and coordinate systems before conversion')
                if keyword == '*NODE':
                    if set(opts) - {'NSET', 'SYSTEM'} or opts.get('SYSTEM','R').upper() != 'R':
                        raise ValueError('NODE: only global rectangular coordinates are supported')
                    parser = NodeParser()
                    for row in rows:
                        nid = int(row.split(',')[0])
                        if nid in df.node:
                            raise ValueError(f'Duplicate node {nid}')
                        parser.parse(row, version)
                        if 'NSET' in opts:
                            nodes.setdefault(opts['NSET'].upper(), []).append(nid)
                elif keyword == '*ELEMENT':
                    ElementParser().parse(opts, rows, df, elements)
                elif keyword == '*MASS':
                    if set(opts) != {'ELSET'} or len(rows) != 1:
                        raise ValueError('MASS: only isotropic point mass is supported')
                    masses.append((opts['ELSET'].upper(),float(rows[0].split(',')[0])))
                elif keyword == '*STATIC':
                    from core.fea.model.lsdyna.control_termination import ControlTermination
                    values = [v.strip() for v in rows[0].split(',')]
                    if len(values)>1 and values[1]:
                        df.control_termination[1] = ControlTermination(uid=1,endtim=float(values[1]))
                elif keyword == '*SURFACE' and opts.get('TYPE','').upper() == 'NODE':
                    node_surfaces[opts['NAME'].upper()] = [r.split(',')[0].strip().upper() for r in rows]
                elif keyword == '*COUPLING':
                    coupling = (int(opts['REF NODE']), opts['SURFACE'].upper())
                elif keyword == '*KINEMATIC' and coupling:
                    dofs = set()
                    for row in rows or ['1,6']:
                        values = [v.strip() for v in row.split(',')]
                        first = int(values[0]) if values[0] else 1
                        last = int(values[1]) if len(values)>1 and values[1] else first
                        if not 1 <= first <= last <= 6:
                            raise ValueError('KINEMATIC: invalid DOF range')
                        dofs.update(range(first,last+1))
                    couplings.append((*coupling, dofs))
                    coupling = None
                elif keyword == '*ELSET':
                    ElsetParser().parse(opts, rows, elements)
                elif keyword == '*NSET':
                    NsetParser().parse(opts, rows, nodes)
                elif keyword in ('*BOUNDARY', '*INITIAL CONDITIONS'):
                    conditions.append((keyword, opts, rows, location, in_step))
                elif keyword in ('*SHELL SECTION', '*SOLID SECTION'):
                    sections.append((keyword, opts, rows, location))
                elif keyword in __import__('core.fea.abaqus.parser.interaction_parser', fromlist=['KEYWORDS']).KEYWORDS:
                    continue
                elif keyword not in ('*MATERIAL', '*DENSITY', '*ELASTIC', '*PLASTIC', '*HEADING', '*AMPLITUDE'):
                    unconverted(f'{keyword}: analysis/keyword data is not converted', source=location)
        except Exception as error:
            raise FeaInputError(f'{location}: {error}') from error
    for keyword, opts, rows, location in sections:
        try:
            with source_scope(location):
                pid = len(df.part) + 1
                parser = ShellSectionParser() if keyword == '*SHELL SECTION' else SolidSectionParser()
                section = parser.parse(opts, rows, pid)
                mid = materials[opts['MATERIAL'].upper()]
                df.part[pid] = Part(uid=pid, secid=pid, mid=mid, name=opts['ELSET'])
                shell = keyword == '*SHELL SECTION'
                store = df.section_shell if shell else df.section_solid
                store[pid] = section
                mesh = df.element_shell if shell else df.element_solid
                for eid in resolve(elements, opts['ELSET'].upper()):
                    if eid not in mesh:
                        raise ValueError(f'Section references missing or incompatible element {eid}')
                    if mesh[eid].pid:
                        raise ValueError(f'Element {eid} belongs to overlapping sections')
                    mesh[eid].pid = pid
        except Exception as error:
            raise FeaInputError(f'{location}: {error}') from error
    for name in nodes:
        sid = len(df.set_node_list)+1
        group = SetNodeList(uid=sid, name=name)
        group.ids = resolve(nodes, name)
        df.set_node_list[sid] = group
    for name, mass in masses:
        import math
        if not math.isfinite(mass) or mass < 0:
            raise FeaInputError(f'Invalid point mass {mass}')
        for eid in resolve(elements,name):
            if eid not in df.storge['element_mass']:
                raise FeaInputError(f'MASS references incompatible element {eid}')
            df.storge['element_mass'][eid].mass = mass
    for reference, surface, dofs in couplings:
        from .interaction_parser import add_coupling
        selected = set()
        for name in node_surfaces[surface]:
            selected.update([int(name)] if name.isdecimal() else resolve(nodes,name))
        add_coupling(df, reference, sorted(selected), dofs)
    for keyword, opts, rows, location, in_step in conditions:
        try:
            with source_scope(location):
                if keyword == '*BOUNDARY' and (in_step or opts):
                    from .motion_parser import parse_boundary
                    parse_boundary(opts,rows,df,nodes,amplitudes,source_metadata)
                else:
                    parser = BoundaryParser() if keyword == '*BOUNDARY' else InitialConditionsParser()
                    parser.parse(opts, rows, df, nodes)
        except Exception as error:
            raise FeaInputError(f'{location}: {error}') from error
    from .interaction_parser import parse_interactions
    parse_interactions(content, df, elements, nodes, options)
    rebuild_indices(df)


def restore_metadata(deck):
    import json, math
    from core.fea.model.lsdyna.initial_velocity_node import InitialVelocityNode
    from core.fea.model.lsdyna.control_termination import ControlTermination
    found = False
    for record in deck.lines:
        text = record.text.strip()
        if text.startswith('** CIRCLECIRCLE2_INITIAL_VELOCITY '):
            nid, components = json.loads(text.split(' ', 2)[2])
            if not isinstance(nid, int) or nid <= 0 or len(components) != 6 or not all(math.isfinite(v) for v in components):
                raise FeaInputError(f'{record.location}: invalid velocity metadata')
            df.storge['initial_velocity_node'][nid] = InitialVelocityNode(nid, tuple(components))
            found = True
        elif text.startswith('** CIRCLECIRCLE2_MOTION '):
            from .motion_parser import add_motion
            add_motion(df,*json.loads(text.split(' ',2)[2]))
            found = True
        elif text.startswith('** CIRCLECIRCLE2_DURATION '):
            end = float(text.split(' ', 2)[2])
            if not math.isfinite(end) or end <= 0:
                raise FeaInputError(f'{record.location}: invalid duration metadata')
            df.control_termination[1] = ControlTermination(uid=1, endtim=end)
    return found
