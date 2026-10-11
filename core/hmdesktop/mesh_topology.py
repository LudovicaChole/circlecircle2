"""Pure mesh adjacency helpers, usable without a HyperMesh installation."""
from collections import defaultdict


def connected_regions(connectivity):
    neighbours = defaultdict(set)
    for eid, nodes in connectivity.items():
        for a, b in zip(nodes, nodes[1:]+nodes[:1]):
            neighbours[tuple(sorted((a, b)))].add(eid)
    adjacency = defaultdict(set)
    for members in neighbours.values():
        for eid in members:
            adjacency[eid].update(members-{eid})
    remaining, regions = set(connectivity), []
    while remaining:
        frontier, region = {remaining.pop()}, set()
        while frontier:
            region.update(frontier)
            following = set().union(*(adjacency[eid] for eid in frontier)) & remaining
            remaining.difference_update(following)
            frontier = following
        regions.append(region)
    return regions


def edge_rows(connectivity, seed_edges, count):
    by_edge = defaultdict(set)
    for eid, nodes in connectivity.items():
        for a, b in zip(nodes, nodes[1:]+nodes[:1]):
            by_edge[tuple(sorted((a,b)))].add(eid)
    seen, frontier, rows = set(), set(seed_edges), []
    for _ in range(count):
        row = set().union(*(by_edge.get(edge,set()) for edge in frontier))-seen if frontier else set()
        if not row:
            break
        rows.append(row)
        seen.update(row)
        frontier = {tuple(sorted((a,b))) for eid in row for a,b in
                    zip(connectivity[eid], connectivity[eid][1:]+connectivity[eid][:1])}
    return rows

