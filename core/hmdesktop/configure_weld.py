"""Explicit Seam Quad parameters; native batch defaults contain zero weld sizes."""
from .tcl_bridge import run, value


def configure_weld(connector, model, settings, log, cad_gap=0.0, joint=None):
    import hm.entities as ent
    # Documented integer detail setter: solver 9 was verified as lsdyna in HM 2026.
    # Its string setter silently leaves the solver as "none" in this version.
    run(f'*CE_DetailSetInt {connector} ce_fesolver 9 0 0')
    if run(f'hm_ce_detailget {connector} string ce_fesolver') != 'lsdyna':
        raise ValueError('Unable to initialize the LS-DYNA connector solver.')
    ce = ent.Connector(model, connector)
    links = [int(i) for i in run(f'hm_ce_getlinkentities {connector} COMPONENTS').split()]
    if len(links) != 2:
        raise ValueError(f'Connector {connector}: expected two resolved component links, got {links}')
    thicknesses = {cid: float(run(f'hm_getthickness comps {cid}')) for cid in links}
    if min(thicknesses.values()) <= 0:
        raise ValueError(f'Connector {connector}: a linked component has no thickness.')
    ce.ce_bl_connection_ang = 10.0
    ce.ce_lt_connection_ang = 10.0
    ce.ce_ltb_use_extension = True
    ce.ce_ltb_extension_ang = 10.0
    # Width is an explicit configurable modelling assumption, not inferred weld CAD.
    width = settings['weld_width']
    factor = width / max(thicknesses.values())
    for direction in ('wb', 'wh', 'wv'):
        setattr(ce, f'ce_ltb_dimensioning_{direction}_factor', factor)
    ce.ce_ltb_connectivity = 'imprint'
    ce.ce_ltb_weld_shape_l = 'angled'
    ce.ce_ltb_weld_shape_t = 'angled'
    ce.ce_ltb_dimensioning_scheme = 'user input'
    ce.ce_ltb_dimensioning_llh = 'by angle'
    ce.ce_ltb_dimensioning_llh_value = 45.0
    # Equal horizontal/vertical legs give a 45-degree right-angle T fillet.
    # The realized geometry is independently checked against the 35..55 limit.
    ce.ce_ltb_dimensioning_lth = 'by length'
    ce.ce_ltb_dimensioning_lth_value = width
    ce.ce_ltb_dimensioning_ltv = 'by length'
    ce.ce_ltb_dimensioning_ltv_value = width
    ce.ce_ltb_dimensioning_lb = 'by edges' if joint == 'BUT' else 'by length'
    ce.ce_ltb_dimensioning_lb_value = width + cad_gap
    ce.ce_ltb_dimensioning_edge_treatment = True
    ce.ce_ltb_dimensioning_edge_trim = 'cut'
    ce.ce_ltb_edge_treatment_limit = 0.5
    if joint == 'BUT':
        # First stitch the existing edges. A complete 4 mm row from one parent
        # is then reassigned to the weld by repair_butt_weld.
        ce.ce_ltb_dimensioning_use_edge = False
        ce.ce_ltb_dimensioning_edge_treatment = False
        ce.ce_ltb_edge_treatment = False
        ce.ce_ltb_use_extension = False
        if cad_gap > 1e-8:
            ce.ce_ltb_dimensioning_lb = 'by length'
            ce.ce_ltb_dimensioning_lb_value = cad_gap + 1e-6
    ce.ce_ltb_haz_all = 'input'
    ce.ce_ltb_haz_all_length = settings['element_size'] * settings['haz_layers']
    # Use the thinner parent's section for the weld, preserving positive thickness.
    parent = min(thicknesses, key=thicknesses.get)
    prop = ent.Property(model, int(value('comps', parent, 'propertyid')))
    for shape in ('straight', 'angled', 'vertical', 'capped'):
        setattr(ce, f'ce_ltb_{shape}_quad_prop', 'PID')
        setattr(ce, f'ce_ltb_{shape}_quad_prop_select', prop)
        setattr(ce, f'ce_ltb_{shape}_quad_factor', 1.0)
    log.info('Connector %s: links %s; weld width %s mm, section thickness %s mm; imprint enabled',
             connector, links, width, thicknesses[parent])
    return links
