"""Common mesh records and indices shared by all source solvers."""
from core.fea.validation import FeaInputError
from utilities.source_location import diagnostic


def insert(store, record):
    if record.uid in store:
        raise FeaInputError(f'Duplicate identifier {record.uid}')
    store[record.uid] = record


def rebuild_indices(df):
    for value in (df.storge_part_element, df.storge_part_node_id, df.storge_part_node_xyz):
        value.clear()
    df.node_tensor[:] = [[n.uid, n.x, n.y, n.z] for n in df.node.values()]
    df.storge_node_id[:] = list(df.node)
    df.element_shell_tensor.clear()
    df.element_solid_tensor.clear()
    for store, count, tensor in ((df.element_shell, 4, df.element_shell_tensor),
                                 (df.element_solid, 8, df.element_solid_tensor)):
        for element in store.values():
            nodes = [getattr(element, f'n{i}') for i in range(1, count+1)]
            # Subtracting a dict_keys view constructs a set of the entire mesh
            # for every element. Connectivity has only four/eight entries.
            missing = {nid for nid in nodes if nid not in df.node}
            if missing:
                raise FeaInputError(diagnostic(f'Element {element.uid}: missing nodes {sorted(missing)}', element))
            tensor.append([element.uid, element.pid, *nodes])
            df.storge_part_element.setdefault(element.pid, []).append(element)
            df.storge_part_node_id.setdefault(element.pid, set()).update(nodes)
            df.storge_part_node_xyz.setdefault(element.pid, set()).update(df.node[n].xyz for n in nodes)


def split_shell_thickness(df):
    """Element H overrides become homogeneous sections, preserving thickness.

    Abaqus sections apply to ELSETs; splitting by H avoids assigning one part's
    thickness to every element. Source element and node identifiers are retained.
    """
    from copy import copy
    groups = {}
    for element in df.element_shell.values():
        h = getattr(element, 'thickness', 0)
        if h <= 0:
            continue
        part = df.part.get(element.pid)
        if part is None or part.secid not in df.section_shell:
            continue
        if h == df.section_shell[part.secid].t1:
            continue
        key = (element.pid, h)
        if key not in groups:
            pid = max(df.part, default=0) + 1
            sid = max([*df.section_shell, *df.section_solid], default=0) + 1
            new_part, section = copy(part), copy(df.section_shell[part.secid])
            new_part.uid, new_part.secid = pid, sid
            new_part.name = f'{part.name}_H{h:g}'
            section.uid, section.name = sid, f'p_shell_{sid}'
            section.t1 = section.t2 = section.t3 = section.t4 = h
            df.part[pid], df.section_shell[sid] = new_part, section
            groups[key] = pid
        element.pid = groups[key]
