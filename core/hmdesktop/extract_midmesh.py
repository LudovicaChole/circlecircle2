"""Direct extrusion midmesh; never accept an empty native result."""
from .tcl_bridge import ids, mark, strings, run


def extract_midmesh(solid, size):
    before = set(ids('elems'))
    mark('solids', [solid])
    n = strings([f'ExtractionSize: {size}', f'TargetElementSize: {size}',
                 f'MinimumSize: {size/2}', 'Method: Extrusion', 'MeshType: mixed'])
    run(f'*midmesh_extract solids 1 1 {n}')
    result = sorted(set(ids('elems')) - before)
    if not result:
        raise ValueError(f'Solid {solid}: native extrusion midmesh produced no elements.')
    return result
