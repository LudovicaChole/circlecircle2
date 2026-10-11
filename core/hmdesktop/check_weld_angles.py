"""Check actual shell face angles at welded parent edges, independent of CE settings."""
import math


class WeldAngleError(ValueError):
    def __init__(self, message, lines):
        super().__init__(message)
        self.lines = lines


def face_normal(points):
    # Newell normal uses every corner, including mildly warped quads.
    normal = [0., 0., 0.]
    for a, b in zip(points, points[1:]+points[:1]):
        normal[0] += (a[1]-b[1])*(a[2]+b[2])
        normal[1] += (a[2]-b[2])*(a[0]+b[0])
        normal[2] += (a[0]-b[0])*(a[1]+b[1])
    length = math.sqrt(sum(v*v for v in normal))
    if length < 1e-12:
        raise ValueError('Cannot evaluate a degenerate weld/parent element.')
    return tuple(v/length for v in normal)


def plane_angle(a, b):
    return math.degrees(math.acos(min(1., abs(sum(x*y for x,y in zip(a,b))))))


def check_weld_angles(reports, log):
    from .tcl_bridge import ids, run
    wanted = {cid: r for r in reports for cid in r.get('weld_components', [])
              if r.get('joint') != 'BUT'}
    if not wanted:
        return
    ids('elems')
    raw = run('set c2rows {}; set c2nodes {}; foreach eid [hm_getmark elems 1] {'
              'set ns [hm_getvalue elems id=$eid dataname=nodes]; '
              'lappend c2rows "$eid [hm_getvalue elems id=$eid dataname=collector.id] $ns"; '
              'foreach nid $ns {dict set c2nodes $nid 1}}; join $c2rows "\\n"')
    elements = [list(map(int, row.split())) for row in raw.splitlines()]
    raw = run('set c2rows {}; foreach nid [dict keys $c2nodes] {'
              'lappend c2rows "$nid [hm_getvalue nodes id=$nid dataname=x] '
              '[hm_getvalue nodes id=$nid dataname=y] [hm_getvalue nodes id=$nid dataname=z]"}; '
              'join $c2rows "\\n"')
    nodes = {int(row[0]):list(map(float,row[1:])) for line in raw.splitlines() if (row := line.split())}
    edges = {}
    normals = {}
    welds = []
    for eid, cid, *ns in elements:
        if len(ns) not in (3,4):
            continue
        normals[eid] = face_normal([nodes[n] for n in ns])
        if cid in wanted:
            welds.append((eid,cid,ns))
        else:
            for a,b in zip(ns,ns[1:]+ns[:1]):
                edges.setdefault(tuple(sorted((a,b))), []).append(eid)
    angles, failures, bad_lines = [], [], set()
    for eid,cid,ns in welds:
        neighbours = {other for a,b in zip(ns,ns[1:]+ns[:1])
                      for other in edges.get(tuple(sorted((a,b))), [])}
        if not neighbours:
            failures.append((eid, 'no shared parent edge'))
            bad_lines.add(wanted[cid]['line'])
        for other in neighbours:
            angle = plane_angle(normals[eid], normals[other])
            angles.append(angle)
            if not 35.-1e-6 <= angle <= 55.+1e-6:
                failures.append((eid, round(angle,3)))
                bad_lines.add(wanted[cid]['line'])
    if angles:
        log.info('Actual fillet weld angles: %.3f to %.3f degrees; required 35 to 55 degrees.', min(angles),max(angles))
    if failures:
        raise WeldAngleError(f'Fillet weld angle validation failed: {failures[:12]}; '
                             f'{len(failures)} failed edge checks. Required 45 +/- 10 degrees.', bad_lines)
