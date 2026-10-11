"""Shared component classification for target numerical controls."""


def deformable_parts(df):
    """Exclude rigid materials and complete rigid node selections, not partial ties."""
    rigid_nodes = []
    for body in df.constrained_nodal_rigid_body.values():
        if getattr(body, 'coupled_dofs', {1, 2, 3, 4, 5, 6}) != {1, 2, 3, 4, 5, 6}:
            continue
        group = df.set_node_list.get(body.sid)
        if group:
            rigid_nodes.append(set(group.ids))
    for part in df.part.values():
        if df.material[part.mid].tag == 'rigid':
            continue
        nodes = set(df.storge_part_node_id.get(part.uid, ()))
        if nodes and any(nodes <= selected for selected in rigid_nodes):
            continue
        yield part
