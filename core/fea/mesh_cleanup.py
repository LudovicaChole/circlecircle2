"""Remove topologically identical solids before generating elements/contact faces."""
from core.fea.abaqus.translator.contact_surface import ContactSurface
from utilities.logger import logger


def remove_duplicate_solids(df):
    seen, deleted = {}, {}
    surface = ContactSurface(df)
    for eid, element in list(df.element_solid.items()):
        # Compare face topology, not coordinates or just the set of vertices.
        signature = (element.format, tuple(sorted(tuple(sorted(face[2]))
                                                  for face in surface._element_faces(element))))
        if signature in seen:
            kept = seen[signature]
            deleted[eid] = kept
            del df.element_solid[eid]
            logger.warning(f'Duplicate solid element {eid} (part {element.pid}) deleted; retained element {kept}', source=element)
        else:
            seen[signature] = eid
    if not deleted:
        return deleted
    for pid, elements in df.storge_part_element.items():
        df.storge_part_element[pid] = [e for e in elements if e.uid not in deleted or e.format in ('s3', 's4')]
    df.element_solid_tensor[:] = [row for row in df.element_solid_tensor if row[0] not in deleted]
    df.element_solid_surface_tensor[:] = [row for e in df.element_solid.values() for row in e.surface_tensor]
    for selection in df.set_solid_list.values():
        selection.ids = list(dict.fromkeys(deleted.get(int(v), int(v)) for v in selection.ids))
    return deleted
