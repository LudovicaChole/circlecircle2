"""Connectivity helpers for turning a parent edge row into a weld strip."""


def merge_edge_quad(weld, parent):
    """Extend a weld quad across its neighbouring parent quad without moving nodes.

    The caller retains the weld element, replaces its connectivity with the
    returned corners, and removes the consumed parent quad. This preserves the
    outer shared boundary with the next parent row.
    """
    weld, parent = tuple(weld), tuple(parent)
    if len(weld) != 4 or len(parent) != 4 or len(set(weld)) != 4 or len(set(parent)) != 4:
        raise ValueError('An edge weld strip requires two non-degenerate quadrilaterals.')
    shared = set(weld).intersection(parent)
    if len(shared) != 2:
        raise ValueError('Weld and parent must share exactly one complete edge.')
    for quad in (weld, parent):
        if not any({a,b} == shared for a,b in zip(quad,quad[1:]+quad[:1])):
            raise ValueError('Shared nodes are not an edge.')
    replacement = {}
    for node in shared:
        index = parent.index(node)
        replacement[node] = next(n for n in (parent[index-1],parent[(index+1)%4]) if n not in shared)
    result = tuple(replacement.get(node,node) for node in weld)
    if len(set(result)) != 4:
        raise ValueError('Extending the weld would collapse its outer edge.')
    return result
