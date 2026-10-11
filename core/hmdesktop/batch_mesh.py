"""4 mm mixed first-order BatchMesh, with native cleanup enabled."""
from .tcl_bridge import ids, mark, strings, run


def batch_mesh(surfaces, size):
    before = set(ids('elems'))
    mark('surfs', surfaces)
    n = strings([f'elem_size={size} min_elem_size={size/2} max_elem_size={size*1.5}',
                 'elem_type=2 elem_order=1 params_generate_mode=shell', 'no_remove_holes=1'])
    run(f'*hm_batchmesh2 surfs 1 1 {n} dummy dummy')
    result = sorted(set(ids('elems')) - before)
    if not result:
        raise ValueError('BatchMesh produced no elements.')
    return result
