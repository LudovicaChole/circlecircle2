"""CAD gap checks before connector searches on offset midsurface meshes.

AABB distance rejects separated bodies; native CAD edge/face distances refine
remaining pairs. HyperMesh thin-solid proximity supplies LAP/BUT/TEE labels.
"""
from itertools import combinations
from math import sqrt


def box_distance(a, b):
    return sqrt(sum(max(0., a[i]-b[i+3], b[i]-a[i+3])**2 for i in range(3)))


def find_weld_pairs(solids, log, tolerance=0.5):
    from .tcl_bridge import run, mark
    geometry = {}
    for sid in solids:
        mark('solids', [sid])
        faces = [int(v) for v in run(f'hm_getsurfacesfromsolid {sid}').split()]
        edges = run('set c2edges {}; foreach s {'+' '.join(map(str, faces))+
                    '} {foreach loop [hm_getsurfaceedges $s] {lappend c2edges {*}$loop}}; '
                    'lsort -integer -unique $c2edges').split()
        geometry[sid] = (list(map(float, run('hm_getboundingbox solids 1 0 0 0').split())), faces, edges)
    mark('solids', solids)
    labels = {}
    try:
        rows = run('set c2rows {}; foreach p [hm_findthinsolidproximity solids 1] '
                   '{lappend c2rows "[join [lindex $p 0] ,]|[lindex $p 1]|[lindex $p 2]"}; '
                   'join $c2rows "\\n"')
        for row in rows.splitlines():
            pair, label, area = row.split('|')
            pair = tuple(sorted(map(int, pair.split(','))))
            if float(area) > labels.get(pair, ('', -1))[1]:
                labels[pair] = (label, float(area))
    except RuntimeError:
        log.warning('Native joint classification unavailable; automatic seams require native connector classification.')
    pairs = {}
    for a, b in combinations(solids, 2):
        if box_distance(geometry[a][0], geometry[b][0]) > tolerance:
            continue
        gap = float('inf')
        # Both directions matter: the nearest edge can belong to either body.
        for source, target in ((a,b), (b,a)):
            for edge in geometry[source][2]:
                for face in geometry[target][1]:
                    values = run(f'hm_getclosestpointsbetweenlinesurface {edge} {face}').split()
                    if len(values) == 7:
                        gap = min(gap, float(values[-1]))
                    elif values and len(values) % 6 == 0:
                        gap = 0.0
                    if gap < 1e-8:
                        break
                if gap < 1e-8:
                    break
            if gap < 1e-8:
                break
        key = tuple(sorted((a,b)))
        log.info('CAD bodies %s / %s: minimum edge/face gap %.6g mm; welding limit %.3g mm', a,b,gap,tolerance)
        if gap <= tolerance + 1e-8:
            pairs[key] = dict(gap=gap, kind=labels.get(key, ('AUTO',0))[0])
    return pairs
