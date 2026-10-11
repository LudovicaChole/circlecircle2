"""Reject FE data before any meshing; identify genuine standalone seam lines."""
from .tcl_bridge import ids, run


def validate_geometry():
    forbidden = ('nodes', 'elems', 'mats', 'props', 'loads', 'loadcols',
                 'loadsteps', 'groups', 'sets', 'connectors', 'equations', 'systems', 'curves')
    found = {entity: len(items) for entity in forbidden if (items := ids(entity))}
    if found:
        raise ValueError('hwx_mesh requires geometry only (points/lines/surfaces/solids); '
                         'remove existing FE data: ' + str(found))
    solids, surfaces = ids('solids'), ids('surfs')
    if not solids and not surfaces:
        raise ValueError('No surfaces or solids found to mesh.')
    seams = [uid for uid in ids('lines') if int(run(f'hm_getlinetype {uid}')) == 0]
    return solids, surfaces, seams
