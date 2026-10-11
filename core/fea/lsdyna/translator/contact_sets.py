"""Use existing shell elements for automatic contacts whenever possible.

Automatic shell contacts are two-sided. A complete shell part selection is
equivalent to a part selection; a subset is represented by a shell element set.
Solid faces and tied contact surfaces retain explicit segment geometry.
"""
from collections import defaultdict
from types import SimpleNamespace


def prepare_contact_sets(df):
    face_index = defaultdict(list)
    by_part = defaultdict(set)
    solid_parts = {element.pid for element in df.element_solid.values()}
    solid_nodes = defaultdict(set)
    for eid, element in df.element_solid.items():
        for i in range(1, 9):
            nid = getattr(element, f'n{i}', 0)
            if nid:
                solid_nodes[nid].add(eid)
    for eid, element in df.element_shell.items():
        nodes = tuple(getattr(element, f'n{i}') for i in range(1, 4 if element.format == 's3' else 5))
        face_index[frozenset(nodes)].append(eid)
        by_part[element.pid].add(eid)
    mapping = {}
    for sid, group in df.set_segment.items():
        selected = set()
        for face in group.segments:
            face_key = frozenset(face)
            # A shell coincident with a solid must not absorb a solid-face
            # selection. Conservatively retain explicit segments in that case.
            touches_solid = bool(face_key) and bool(set.intersection(*(solid_nodes[n] for n in face_key)))
            matches = () if touches_solid else face_index.get(face_key, ())
            if len(matches) != 1:
                break
            selected.add(matches[0])
        else:
            if not selected:
                continue
            pids = {df.element_shell[eid].pid for eid in selected}
            complete = all(pid in df.part and by_part[pid] <= selected and pid not in solid_parts for pid in pids)
            if complete and len(pids) == 1:
                mapping[sid] = (next(iter(pids)), 3)
            elif complete:
                store = df.set_part_list
                existing = next((uid for uid, obj in store.items() if set(obj.ids) == pids), None)
                uid = existing if existing is not None else max(store, default=0) + 1
                if existing is None:
                    store[uid] = SimpleNamespace(uid=uid, ids=sorted(pids), name=group.name)
                mapping[sid] = (uid, 2)
            else:
                store = df.set_shell_list
                existing = next((uid for uid, obj in store.items() if set(obj.ids) == selected), None)
                uid = existing if existing is not None else max(store, default=0) + 1
                if existing is None:
                    store[uid] = SimpleNamespace(uid=uid, ids=sorted(selected), name=group.name)
                mapping[sid] = (uid, 1)
    consumed = set()
    for store in (df.contact_automatic_surface_to_surface_id, df.contact_automatic_single_surface_id):
        for obj in store.values():
            for id_field, type_field in (('ssid', 'sstyp'), ('msid', 'mstyp')):
                sid = getattr(obj, id_field)
                if getattr(obj, type_field) == 0 and sid in mapping:
                    setattr(obj, id_field, mapping[sid][0])
                    setattr(obj, type_field, mapping[sid][1])
                    consumed.add(sid)
    # Unused Abaqus surfaces also have element sets; emitting their display
    # segments adds no solver semantics. Retain all solid/edge and tied faces.
    retained = {tie.master.sid for tie in df.storge['surface_ties'].values()}
    return {sid for sid, group in df.set_segment.items()
            if sid not in mapping or sid in retained or
            (sid not in consumed and not getattr(group, 'abaqus_surface', False))}
