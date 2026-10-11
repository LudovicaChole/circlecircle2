"""Resolve Abaqus coupling, surface, contact and history selections after mesh parsing."""
import math
from types import SimpleNamespace
from core.fea.conversion_notes import unconverted
from core.fea.model.lsdyna.set_segment import SetSegment
from core.fea.model.lsdyna.set_node_list import SetNodeList
from core.fea.model.lsdyna.constrained_nodal_rigid_body import ConstrainedNodalRigidBody
from core.fea.model.lsdyna.database_history_node import DatabaseHistoryNode
from core.fea.abaqus.translator.contact_surface import ContactSurface
from .elset_parser import resolve

KEYWORDS = {'*KINEMATIC COUPLING', '*SURFACE', '*SURFACE INTERACTION', '*SURFACE BEHAVIOR', '*FRICTION', '*CONTACT PAIR', '*TIE', '*NODE OUTPUT',
            '*CONTACT', '*CONTACT INCLUSIONS', '*CONTACT PROPERTY ASSIGNMENT', '*CONTACT EXCLUSIONS'}
CODES = {frozenset(v): k for k, v in {0: (), 1: (1,), 2: (2,), 3: (3,), 4: (1, 2), 5: (2, 3), 6: (1, 3), 7: (1, 2, 3)}.items()}


def select_nodes(label, nodes):
    return [int(label)] if label.strip().isdecimal() else resolve(nodes, label.upper())


def parse_interactions(content, df, elements, nodes, options):
    surfaces, interactions, pending, property_name = {}, {}, [], None
    for location, header, rows in content:
        keyword, opts = options(header)
        if keyword not in KEYWORDS:
            continue
        if keyword in ('*CONTACT', '*CONTACT INCLUSIONS', '*CONTACT PROPERTY ASSIGNMENT', '*CONTACT EXCLUSIONS'):
            continue
        with __import__('utilities.source_location', fromlist=['source_scope']).source_scope(f'{location}: {keyword}'):
            if keyword == '*SURFACE':
                name = opts['NAME'].upper()
                if name in surfaces:
                    raise ValueError(f'Duplicate surface {name}')
                kind = opts.get('TYPE', 'ELEMENT').upper()
                if kind == 'NODE':
                    selected = sorted({n for row in rows for n in select_nodes(row.split(',')[0].strip(), nodes)})
                    surfaces[name] = SimpleNamespace(nodes=selected, sid=None, facets=[])
                    continue
                if kind != 'ELEMENT':
                    raise ValueError(f'SURFACE {name}: unsupported type {kind}')
                facets, shell_ids, solid_ids = [], set(), set()
                for row in rows:
                    vals = [v.strip().upper() for v in row.split(',')]
                    ids = [int(vals[0])] if vals[0].isdecimal() else resolve(elements, vals[0])
                    side = vals[1] if len(vals) > 1 else ''
                    for eid in ids:
                        obj = df.element_shell.get(eid) or df.element_solid.get(eid)
                        if obj is None:
                            raise ValueError(f'SURFACE {name}: missing element {eid}')
                        order = ContactSurface.connectivity[obj.format]
                        ns = tuple(getattr(obj, f'n{i}') for i in order)
                        if obj.format in ('s3', 's4'):
                            if side not in ('', 'SPOS', 'SNEG'):
                                raise ValueError(f'SURFACE {name}: shell face {side} is not mapped')
                            facets.append(ns[::-1] if side == 'SNEG' else ns)
                            shell_ids.add(eid)
                        else:
                            faces = ContactSurface.solid_faces[obj.format]
                            if not side.startswith('S') or not side[1:].isdecimal() or not 1 <= int(side[1:]) <= len(faces):
                                raise ValueError(f'SURFACE {name}: an explicit solid face is required')
                            facets.append(tuple(ns[i-1] for i in faces[int(side[1:])-1]))
                            solid_ids.add(eid)
                sid = max(df.set_segment, default=0)+1
                group = SetSegment(uid=sid, name=name)
                group.abaqus_surface = True
                group.segments = list(dict.fromkeys(facets))
                if not group.segments:
                    raise ValueError(f'SURFACE {name}: empty selection')
                df.set_segment[sid] = group
                surfaces[name] = SimpleNamespace(sid=sid, facets=group.segments,
                                                nodes=sorted({n for face in facets for n in face}))
                for store, selected in ((df.set_shell_list, shell_ids), (df.storge['set_solid_list'], solid_ids)):
                    if selected:
                        uid = max(store, default=0)+1
                        store[uid] = SimpleNamespace(uid=uid, ids=sorted(selected), name=name)
            elif keyword == '*SURFACE INTERACTION':
                property_name = opts['NAME'].upper()
                interactions[property_name] = 0.0
            elif keyword == '*SURFACE BEHAVIOR':
                if property_name is None:
                    raise ValueError('SURFACE BEHAVIOR: missing surface interaction')
                if rows or set(opts)-{'PRESSURE-OVERCLOSURE'} or opts.get('PRESSURE-OVERCLOSURE','HARD').upper() != 'HARD':
                    unconverted('Only hard normal contact is mapped to automatic contact', location)
            elif keyword == '*FRICTION':
                if property_name is None or opts or len(rows) != 1:
                    if property_name is not None:
                        interactions[property_name] = None
                    unconverted('Only constant Coulomb friction is mapped; original data is archived', location)
                    continue
                vals = [float(v) if v.strip() else 0.0 for v in rows[0].split(',')]
                if not vals or not all(math.isfinite(v) for v in vals):
                    raise ValueError('FRICTION: invalid numeric data')
                if any(v != 0 for v in vals[1:]):
                    interactions[property_name] = None
                    unconverted('Dependent friction is not mapped; original data is archived', location)
                    continue
                coefficient = float(vals[0])
                if not math.isfinite(coefficient) or coefficient < 0:
                    raise ValueError('FRICTION: invalid coefficient')
                interactions[property_name] = coefficient
            elif keyword == '*KINEMATIC COUPLING':
                if set(opts)-{'REF NODE'}:
                    unconverted('Local/thermal kinematic coupling is not mapped; original data is archived', location)
                    continue
                ref = select_nodes(opts['REF NODE'], nodes)
                if len(ref) != 1:
                    raise ValueError('KINEMATIC COUPLING: REF NODE must contain exactly one node')
                dependent = {}
                for row in rows:
                    vals = [v.strip() for v in row.split(',')]
                    first = int(vals[1]) if len(vals)>1 and vals[1] else 1
                    last = int(vals[2]) if len(vals)>2 and vals[2] else (first if len(vals)>1 and vals[1] else 6)
                    if not 1 <= first <= last <= 6:
                        raise ValueError('KINEMATIC COUPLING: invalid degree of freedom range')
                    for nid in select_nodes(vals[0], nodes):
                        dependent.setdefault(nid, set()).update(range(first, last+1))
                by_mask = {}
                for nid, dofs in dependent.items():
                    by_mask.setdefault(tuple(sorted(dofs)), []).append(nid)
                for dofs, selected in by_mask.items():
                    add_coupling(df, ref[0], selected, dofs)
            elif keyword == '*NODE OUTPUT':
                selected = select_nodes(opts['NSET'], nodes) if 'NSET' in opts else sorted(df.node)
                uid = max(df.database_history_node, default=0)+1
                group = DatabaseHistoryNode(uid=uid, name=opts.get('NSET', 'ALL_NODES'))
                group.ids = selected
                df.database_history_node[uid] = group
            else:
                pending.append((keyword, opts, rows, location))
    from core.fea.model.lsdyna.contact_automatic_surface_to_surface_id import ContactAutomaticSurfaceToSurfaceID
    from core.fea.model.lsdyna.contact_automatic_single_surface_id import ContactAutomaticSingleSurfaceID
    contacts = []
    for keyword, opts, rows, location in pending:
        for row in rows:
            names = [v.strip().upper() for v in row.split(',')]
            slave = surfaces[names[0]]
            master = surfaces[names[1]] if len(names)>1 and names[1] else slave
            tolerance = float(opts.get('POSITION TOLERANCE', '0'))
            if not math.isfinite(tolerance) or tolerance < 0:
                raise ValueError(f'{keyword}: invalid POSITION TOLERANCE')
            if keyword == '*TIE' or 'TIED' in opts:
                uid = max(df.storge['surface_ties'], default=0)+1
                df.storge['surface_ties'][uid] = SimpleNamespace(uid=uid, name=opts.get('NAME',f'tie_{uid}'),
                    slave=slave, master=master, tolerance=tolerance, adjust=opts.get('ADJUST','YES').upper(), source_context=location)
                continue
            if slave.sid is None or master.sid is None:
                unconverted('Node-based contact pair is archived; element surfaces are required for automatic contact', location)
                continue
            property_name = opts.get('INTERACTION','').upper()
            if property_name and property_name not in interactions:
                raise ValueError(f'{keyword}: undefined surface interaction {property_name}')
            coefficient = interactions.get(property_name, 0.0)
            contacts.append((slave, master, coefficient, location, tolerance))
    from .general_contact_parser import contact_pairs
    contacts.extend((*pair, 0.0) for pair in contact_pairs(content, df, surfaces, interactions, options))
    for slave, master, coefficient, location, tolerance in contacts:
        if slave.sid is None or master.sid is None:
            raise ValueError('General contact requires element surfaces')
        uid = max(set(df.contact_automatic_surface_to_surface_id)|set(df.contact_automatic_single_surface_id),default=0)+1
        self_contact = slave is master
        if coefficient is None:
            raise ValueError(f'Contact at {location}: unsupported friction cannot be replaced with zero friction')
        cls = ContactAutomaticSingleSurfaceID if self_contact else ContactAutomaticSurfaceToSurfaceID
        obj = cls(uid=uid, heading=f'abaqus_contact_{uid}', ssid=slave.sid, msid=0 if self_contact else master.sid,
                  sstyp=getattr(slave,'selection_type',0), mstyp=0 if self_contact else getattr(master,'selection_type',0),
                  fs=coefficient, fd=coefficient, dt=1e20, sst=tolerance, mst=tolerance)
        obj.source_context = location
        obj.contact_thickness = tolerance
        store = df.contact_automatic_single_surface_id if self_contact else df.contact_automatic_surface_to_surface_id
        store[uid] = obj


def add_coupling(df, reference, selected, dofs=tuple(range(1,7))):
    if reference not in df.node or any(n not in df.node for n in selected):
        raise ValueError('Kinematic coupling references missing nodes')
    selected = list(dict.fromkeys([reference]+list(selected)))
    sid = max(df.set_node_list, default=0)+1
    group = SetNodeList(uid=sid, name=f'abaqus_coupling_{reference}_{sid}')
    group.ids = selected
    df.set_node_list[sid] = group
    uid = max(set(df.constrained_nodal_rigid_body)|set(df.part), default=0)+1
    dr = CODES[frozenset({1,2,3}-set(dofs))]
    rr = CODES[frozenset({1,2,3}-{d-3 for d in dofs if d>3})]
    body = ConstrainedNodalRigidBody(uid=uid, pid=uid, sid=sid, pnode=reference, drflag=-dr, rrflag=-rr,
                                    name=group.name)
    body.coupled_dofs = set(dofs)
    df.constrained_nodal_rigid_body[uid] = body
