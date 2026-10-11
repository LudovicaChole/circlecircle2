"""Independent area/thickness volume check catches grossly incomplete midmeshes."""
import math


def polygon_area(points):
    if len(points) < 3:
        return 0.0
    origin = points[0]
    total = 0.0
    for left, right in zip(points[1:-1], points[2:]):
        a = [left[i]-origin[i] for i in range(3)]
        b = [right[i]-origin[i] for i in range(3)]
        cross = (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
        total += math.sqrt(sum(x*x for x in cross))/2
    return total


def check_mesh_coverage(solid, elements, thicknesses, tolerance=0.1):
    from .tcl_bridge import mark, run
    from .mesh_topology import connected_regions
    mark('elems', elements)
    # Fetch in Tcl batches to avoid one Python/native round trip per node.
    raw = run('set c2rows {}; set c2nodes {}; foreach eid [hm_getmark elems 1] {'
              'set ns [hm_getvalue elems id=$eid dataname=nodes]; '
              'lappend c2rows "$eid [hm_getvalue elems id=$eid dataname=collector.id] $ns"; '
              'foreach nid $ns {dict set c2nodes $nid 1}}; join $c2rows "\\n"')
    rows = [list(map(int, row.split())) for row in raw.splitlines() if row.strip()]
    regions = connected_regions({eid: ns for eid, _, *ns in rows})
    if len(regions) != 1:
        raise ValueError(f'Solid {solid}: extraction produced {len(regions)} disconnected shell patches '
                         f'(element counts {sorted(map(len, regions))}).')
    raw = run('set c2rows {}; foreach nid [dict keys $c2nodes] {'
              'lappend c2rows "$nid [hm_getvalue nodes id=$nid dataname=x] '
              '[hm_getvalue nodes id=$nid dataname=y] [hm_getvalue nodes id=$nid dataname=z]"}; '
              'join $c2rows "\\n"')
    nodes = {int(row[0]): list(map(float, row[1:])) for line in raw.splitlines()
             if (row := line.split())}
    shell_volume = sum(polygon_area([nodes[n] for n in ns])*thicknesses[cid]
                       for _, cid, *ns in rows)
    solid_volume = float(run(f'hm_getvolumeofsolid solids {solid}'))
    error = abs(shell_volume-solid_volume)/solid_volume if solid_volume > 0 else math.inf
    report = dict(solid_volume=solid_volume, shell_volume=shell_volume,
                  relative_error=error, connected_regions=len(regions))
    if not math.isfinite(error) or error > tolerance:
        raise ValueError(f'Solid {solid}: midmesh coverage check failed; area × thickness volume '
                         f'{shell_volume:.6g} versus CAD volume {solid_volume:.6g} '
                         f'(difference {error:.1%}, limit {tolerance:.0%}). '
                         'Inspect missing walls, holes or incorrect thickness before accepting this mesh.')
    return report
