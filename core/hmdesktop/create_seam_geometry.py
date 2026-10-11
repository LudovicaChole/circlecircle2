"""Keep a visible CAD seam alongside automatically generated line connectors."""
from .tcl_bridge import run, quote


def create_seam_geometry(model, connector):
    import hm.entities as ent
    points = ent.Connector(model, connector).ce_coords.tolist()
    if len(points) < 2:
        raise ValueError(f'Automatic connector {connector} has no usable seam polyline.')
    # Collapse collinear native sample points, retaining corners on curved seams.
    kept = [points[0]]
    for a,b,c in zip(points,points[1:],points[2:]):
        u,v = [b[i]-a[i] for i in range(3)], [c[i]-b[i] for i in range(3)]
        cross = (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        if sum(x*x for x in cross) > 1e-12 or sum(x*y for x,y in zip(u,v)) <= 0:
            kept.append(b)
    kept.append(points[-1])
    name = f'auto_seam_{connector}'
    run(f'*createentity comps name={quote(name)}')
    run(f'*currentcollector components {quote(name)}')
    lines = []
    for a,b in zip(kept,kept[1:]):
        run('*linecreatestraight '+' '.join(format(x,'.15g') for x in a+b))
        lines.append(int(run('hm_latestentityid lines')))
    return lines
