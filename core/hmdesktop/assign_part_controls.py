"""Assign Part controls without overriding HyperMesh's hourglass defaults."""
from .tcl_bridge import ids, run, value, quote


def assign_part_controls(model, log):
    import hm.entities as ent
    # HyperMesh element configurations, including second-order elements.
    shells = {103, 104, 106, 108}
    solids = {204, 205, 206, 208, 210, 213, 215, 220}
    hourglasses = {}
    report = []
    for cid in ids('comps'):
        elements = ids('elems', f'"by collector id" {cid}')
        if not elements:
            continue
        configurations = {int(value('elems', eid, 'config')) for eid in elements}
        kind = ('shell' if configurations <= shells else
                'solid' if configurations <= solids else None)
        run(f'*setvalue comps id={cid} cardimage=Part')
        component = ent.Component(model, cid)
        if kind:
            if kind not in hourglasses:
                run(f'*createentity hourglass config=101 name={quote("default_"+kind)}')
                hg = ent.Hourglass(model, int(run('hm_latestentityid hourglass')))
                # Do not set controlType, coeff or viscosity coefficients here:
                # the user explicitly selected the installed HyperMesh defaults.
                hourglasses[kind] = hg
                log.info('%s hourglass %s: HyperMesh defaults, IHQ=%s, QH=%s',
                         kind, hg.id, hg.controlType, hg.coeff)
            component.LSD_HGID = hourglasses[kind]
        else:
            run(f'*setvalue comps id={cid} STATUS=1 462={{hourglass 0}}')
        thickness = float(run(f'hm_getthickness comps {cid}')) if kind == 'shell' else 0.0
        if thickness > 4.0:
            component.Part_Option = 6  # Contact
            component.LSD_OPTT = thickness / 2.0
        report.append(dict(component=cid, hourglass=kind, thickness=thickness,
                           contact=thickness > 4.0))
    log.info('Part controls assigned to %s mesh components; hourglass coefficients kept at HyperMesh defaults.', len(report))
    return report
