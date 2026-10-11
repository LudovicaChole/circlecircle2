"""Make a butt weld from one complete 4 mm parent edge row.

The thinner parent supplies the weld strip; both parents retain their next two
rows for HAZ. Shared node IDs and the opposing plate's midsurface offset are
preserved. No symmetric trimming or artificial node movement is performed.
"""
import math
from .check_weld_angles import face_normal, plane_angle
from .weld_edge_strip import merge_edge_quad
from .tcl_bridge import ids, mark, run, value


def repair_butt_weld(reports, components, settings, log):
    welds = {cid for r in reports if r.get('joint') == 'BUT' for cid in r.get('weld_components', [])}
    if not welds:
        return
    parents, weld_elements, nodes = {}, {}, {}
    for cid in set(components) | welds:
        for eid in ids('elems', f'"by collector id" {cid}'):
            ns = tuple(map(int,value('elems',eid,'nodes').split()))
            (weld_elements if cid in welds else parents)[eid] = (cid,ns)
            for n in ns:
                if n not in nodes:
                    nodes[n] = tuple(float(value('nodes',n,a)) for a in ('x','y','z'))
    edge_map = {}
    for eid,(cid,ns) in parents.items():
        for a,b in zip(ns,ns[1:]+ns[:1]):
            edge_map.setdefault(tuple(sorted((a,b))), []).append(eid)
    changes, consumed, widths, selected_comps = {}, set(), [], set()
    for eid,(_,ns) in weld_elements.items():
        shared = [(a,b,edge_map[tuple(sorted((a,b)))][0]) for a,b in zip(ns,ns[1:]+ns[:1])
                  if tuple(sorted((a,b))) in edge_map]
        if len(shared) != 2 or parents[shared[0][2]][0] == parents[shared[1][2]][0]:
            raise ValueError(f'Butt weld {eid}: cannot identify one edge on each parent.')
        normals = [face_normal([nodes[n] for n in parents[parent][1]]) for _,_,parent in shared]
        if plane_angle(*normals) > 10.0:
            raise ValueError(f'Butt weld {eid}: parent plates are not locally parallel.')
        a,b,parent = min(shared, key=lambda edge: (components[parents[edge[2]][0]]['thickness'],
                                                  parents[edge[2]][0]))
        if parent in consumed:
            raise ValueError(f'Parent element {parent}: overlapping weld strips require local remeshing.')
        new_nodes = merge_edge_quad(ns, parents[parent][1])
        far = [n for n in new_nodes if n not in ns]
        inner_center = [(nodes[a][i]+nodes[b][i])/2 for i in range(3)]
        outer_center = [(nodes[far[0]][i]+nodes[far[1]][i])/2 for i in range(3)]
        tangent = [nodes[b][i]-nodes[a][i] for i in range(3)]
        length = math.sqrt(sum(x*x for x in tangent))
        displacement = [outer_center[i]-inner_center[i] for i in range(3)]
        along = sum(displacement[i]*tangent[i]/length for i in range(3))
        width = math.sqrt(max(0.,sum(x*x for x in displacement)-along*along))
        if abs(width-settings['weld_width']) > settings['weld_width']*.05:
            raise ValueError(f'Butt weld {eid}: parent edge row is {width:.6g} mm wide; '
                             f'a {settings["weld_width"]} mm strip requires local remeshing.')
        changes[eid] = new_nodes
        consumed.add(parent)
        selected_comps.add(parents[parent][0])
        widths.append(width)
    # All candidates are checked before any topology is changed.
    for eid,ns in changes.items():
        run(f'*setvalue elems id={eid} nodes={{nodes '+ ' '.join(map(str,ns))+'}')
    mark('elems', consumed)
    run('*deletemark elems 1')
    log.info('Butt weld: converted one parent edge row to weld material; parent components %s, '
             '%s quads, measured strip width %.4f to %.4f mm. HAZ: two subsequent rows on each parent.',
             sorted(selected_comps),len(consumed),min(widths),max(widths))
