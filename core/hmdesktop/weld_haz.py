"""Build exactly two edge-adjacent parent mesh rows beside realized seam quads."""
from .mesh_topology import edge_rows
from .tcl_bridge import value, ids, mark, run, quote


def assign_haz(elements, components, materials, settings, log):
    collectors = {int(value('elems', eid, 'collector.id')) for eid in elements}
    welds = [cid for cid in collectors if 'weld' in value('comps', cid, 'name').lower()]
    if not welds:
        raise ValueError('Native Seam Quad did not create identifiable weld components.')
    seed_edges = set()
    report = {'welds': [], 'haz': []}
    for cid in welds:
        if float(run(f'hm_getthickness comps {cid}')) <= 0:
            raise ValueError(f'Weld component {cid}: no positive shell thickness.')
        mid = materials.assign(cid, settings['weld_material'])
        thickness = float(run(f'hm_getthickness comps {cid}'))
        from .component_names import component_name
        label = component_name(f'weld_{cid}', settings['weld_material'], thickness)
        run(f'*setvalue comps id={cid} name={quote(label)}')
        report['welds'].append(dict(component=cid, material=mid, thickness=thickness,
                                   elements=len(ids('elems', f'"by collector id" {cid}'))))
        for eid in ids('elems', f'"by collector id" {cid}'):
            nodes = [int(n) for n in value('elems', eid, 'nodes').split()]
            seed_edges.update(tuple(sorted((a,b))) for a,b in zip(nodes,nodes[1:]+nodes[:1]))
    connected = 0
    for cid, parent in list(components.items()):
        connectivity = {eid:[int(n) for n in value('elems', eid, 'nodes').split()]
                        for eid in ids('elems', f'"by collector id" {cid}')}
        rows = edge_rows(connectivity, seed_edges, settings['haz_layers'])
        if not rows:
            continue
        if len(rows) != settings['haz_layers']:
            raise ValueError(f'Component {cid}: insufficient mesh for two complete HAZ rows.')
        selected = set.union(*rows)
        name = parent['name']+'_haz'
        prop = int(value('comps', cid, 'propertyid'))
        run(f'*createentity comps cardimage=Part name={quote(name)}')
        new = int(run('hm_latestentityid comps'))
        run(f'*setvalue comps id={new} propertyid={{props {prop}}}')
        mark('elems', selected)
        run(f'*movemark elems 1 {quote(name)}')
        mid = materials.assign(new, (parent['tag'] or 'default_elastic')+'_haz')
        report['haz'].append(dict(component=new, parent=cid, material=mid,
                                 rows=[len(row) for row in rows], elements=len(selected)))
        connected += 1
        log.info('HAZ component %s: %s elements in %s rows, nominal row size %s mm',
                 new,len(selected),len(rows),settings['element_size'])
    if connected < 2:
        raise ValueError('Weld does not share mesh edges with two parent components; inspect native realization.')
    return report
