"""Map original solid thickness to shell properties/components."""
from .tcl_bridge import ids, mark, strings, run, value


def map_thickness(solid, elements, tolerance):
    if not ids('props', '"by name only" t0'):
        run('*createentity props cardimage=SectShll name=t0')
    mark('elems', elements)
    mark('solids', [solid], 2)
    n = strings(['ThicknessOutputOption: PropertyOnComponents2', 'SampleProperty: t0',
                 f'AbsoluteGroupingTolerance: {tolerance}', 'NeedOffset: 0'])
    run(f'*compute_midmesh_thickness elems 1 solids 2 1 {n}')
    components = sorted({int(value('elems', eid, 'collector.id')) for eid in elements})
    result = {}
    for cid in components:
        thickness = float(run(f'hm_getthickness comps {cid}') or 0)
        if thickness <= 0:
            raise ValueError(f'Component {cid}: thickness mapping failed; no positive section thickness.')
        result[cid] = thickness
    return result
