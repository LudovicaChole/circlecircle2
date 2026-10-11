"""Create native seam connectors after meshing; validate FE realization."""
from .tcl_bridge import ids, mark, strings, run, value


def weld_connectors(lines, components, materials, settings, log, weld_pairs=None):
    from .weld_haz import assign_haz
    from .configure_weld import configure_weld
    run('set c2bin [hm_info -appinfo HMBIN_DIR]; '
        '*createstringarray 2 "$c2bin/feconfig.cfg" "$c2bin/DiameterMappingTable.txt"; '
        '*CE_FE_SetCommonDetails 1 2 0.0')
    reports = []
    pending = []
    covered = set()
    def accept(connectors, line):
        for connector in connectors:
            links = [int(i) for i in run(f'hm_ce_getlinkentities {connector} COMPONENTS').split()]
            bodies = {components[c].get('solid') for c in links if c in components}
            pair = tuple(sorted(bodies)) if None not in bodies else ()
            if weld_pairs is not None and (len(pair) != 2 or pair not in weld_pairs):
                log.warning('Seam %s, connector %s skipped: linked bodies %s have no verified CAD gap <= 0.5 mm.', line, connector, pair)
                mark('connectors', [connector]);run('*deletemark connectors 1')
                continue
            if line != 'automatic' and pair and weld_pairs is not None:
                point = run(f'hm_getcoordinatesofpointsonline {line} {{0.5}}').replace('{','').replace('}','')
                distances = []
                for body in pair:
                    faces = run(f'hm_getsurfacesfromsolid {body}')
                    distances.append(float(run(f'hm_getdistancefromnearestsurface {{{point}}} {{{faces}}}').split()[0]))
                allowance = max(components[c]['thickness'] for c in links) + 0.5
                if max(distances) > allowance:
                    log.warning('Line %s is too far from its CAD joint (surface distances %s mm). Replacing it with an automatic seam at the touching bodies.', line, distances)
                    mark('connectors', [connector]);run('*deletemark connectors 1')
                    continue
            covered.add(pair)
            pending.append((connector, line, pair))
    for line in lines:
        before_ce = set(ids('connectors'))
        before_elems = set(ids('elems'))
        mark('lines', [line])
        mark('comps', components, 2)
        n = strings(['link_elems_geom=elems', 'link_rule=now', 'relink_rule=none',
                     'tol_flag=1', 'tol=8.0', f'line_spacing={settings["element_size"]}'])
        run(f'*CE_ConnectorCreateByMark lines 1 seam 2 comps 2 1 {n}')
        connectors = sorted(set(ids('connectors'))-before_ce)
        if not connectors:
            raise ValueError(f'Line {line}: connector creation failed.')
        accept(connectors, line)
    for pair, info in (weld_pairs or {}).items():
        if pair in covered:
            continue
        linked = [cid for cid, data in components.items() if data.get('solid') in pair]
        before_ce = set(ids('connectors'))
        mark('comps', linked)
        radius = max(8.0, 2*max(components[c]['thickness'] for c in linked))
        options = (f'search_radius={radius} pitch={settings["element_size"]} '
                   f'minimum_connector_length={settings["element_size"]} '
                   'exclude_holes_with_radius_less_than=0 create_internal_seams=0')
        from .tcl_bridge import quote
        run(f'*CE_ConnectorCreateByAutoseam components 1 {quote(options)}')
        connectors = sorted(set(ids('connectors'))-before_ce)
        if not connectors:
            raise ValueError(f'Bodies {pair}: CAD gap {info["gap"]:.6g} mm is within tolerance, but no automatic seam could be created.')
        log.info('Bodies %s: %s joint, gap %.6g mm; created %s automatic seam connectors.', pair, info['kind'], info['gap'], len(connectors))
        accept(connectors, 'automatic')
        if pair not in covered:
            raise ValueError(f'Bodies {pair}: automatic seams did not resolve the required body pair.')
        from .create_seam_geometry import create_seam_geometry
        for connector, origin, body_pair in pending:
            if origin == 'automatic' and body_pair == pair:
                generated = create_seam_geometry(materials.model, connector)
                log.info('Automatic connector %s: CAD seam lines %s created.', connector, generated)
    all_new = set()
    for connector, line, pair in pending:
        connectors = [connector]
        before_elems = set(ids('elems'))
        mark('connectors', connectors)
        run('*CE_FE_SetDetails 1 1001 8.0 0 0 0 1 0 128')
        for connector in connectors:
            configure_weld(connector, materials.model, settings, log,
                           (weld_pairs or {}).get(pair, {}).get('gap', 0.0),
                           (weld_pairs or {}).get(pair, {}).get('kind'))
        mark('connectors', connectors)
        # 128 is the installed HyperMesh 2026 feconfig.cfg Seam Quad type.
        n = strings(['ce_connectivity=1'])
        run(f'*CE_FE_RealizeWithDetails 1 seam dyna 1001 128 1 8.0 1 {n}')
        for connector in connectors:
            if run(f'hm_ce_info {connector} state') != 'realized':
                raise ValueError(f'Line {line}, connector {connector}: '
                                 + run(f'hm_ce_errorreport {connector} 1'))
        new_elements = set(ids('elems'))-before_elems
        if not new_elements:
            raise ValueError(f'Line {line}: seam connector produced no weld elements; check links/tolerance.')
        all_new.update(new_elements)
        collectors = {int(value('elems', eid, 'collector.id')) for eid in new_elements}
        weld_components = [cid for cid in collectors if 'weld' in value('comps', cid, 'name').lower()]
        reports.append(dict(line=line, connectors=connectors, bodies=pair,
                            joint=(weld_pairs or {}).get(pair, {}).get('kind', 'AUTO'),
                            weld_components=weld_components))
    if all_new:
        from .repair_butt_weld import repair_butt_weld
        repair_butt_weld(reports, components, settings, log)
        # Defer moving HAZ elements until every connector has imprinted the parents.
        report = assign_haz(all_new.intersection(ids('elems')), components, materials, settings, log)
        reports.append(report)
    from .check_weld_angles import check_weld_angles
    check_weld_angles(reports, log)
    return reports
