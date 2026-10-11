"""Retry misplaced explicit welds using CAD-gated automatic seam detection."""
from .tcl_bridge import ids, marked, value
from .weld_connectors import weld_connectors
from .check_weld_angles import WeldAngleError, check_weld_angles
from .check_mesh_quality import check_mesh_quality


def mesh_welds(seams, components, catalog, settings, log, pairs, directory):
    checkpoint = directory/'before_welding.hm'
    catalog.model.writefile(filename=str(checkpoint), do_not_write_facets=1)
    cache = dict(catalog.cache)
    remaining = list(seams)
    for attempt in range(3):
        if attempt:
            catalog.model.readfile(filename=str(checkpoint), load_cad_geometry_as_graphics=0)
            catalog.cache = dict(cache)
        reports = []
        try:
            reports = weld_connectors(remaining, components, catalog, settings, log, pairs)
            weld_cids = {cid for r in reports for cid in r.get('weld_components', [])}
            anchors = {int(n) for cid in weld_cids for eid in ids('elems', f'"by collector id" {cid}')
                       for n in value('elems', eid, 'nodes').split()}
            check_mesh_quality(ids('elems'), directory, anchors)
            check_weld_angles(reports, log)
            checkpoint.unlink()
            return reports
        except WeldAngleError as error:
            bad = error.lines.intersection(remaining)
            if not bad or attempt == 2:
                raise
            log.warning('Explicit seam angle check failed; retrying lines %s using automatic joint detection.', sorted(bad))
        except ValueError:
            failed_comps = {int(value('elems', eid, 'collector.id')) for eid in marked('elems', 2)}
            bad = {r['line'] for r in reports if failed_comps.intersection(r.get('weld_components', []))
                   and r['line'] in remaining}
            if not bad or attempt == 2:
                raise
            log.warning('Explicit seam quality check failed; retrying lines %s using automatic joint detection.', sorted(bad))
        remaining = [line for line in remaining if line not in bad]
