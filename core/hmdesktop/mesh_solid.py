"""Bounded extraction retries with complete native rollback between methods."""
from .extract_midsurface import extract_midsurface
from .extract_midmesh import extract_midmesh
from .batch_mesh import batch_mesh
from .map_thickness import map_thickness
from .check_mesh_coverage import check_mesh_coverage


def mesh_solid(model, solid, kind, directory, settings, log):
    checkpoint = directory/f'solid_{solid}_checkpoint.hm'
    model.writefile(filename=str(checkpoint), do_not_write_facets=1)
    methods = [('offset+planes', 3), ('offset+planes+sweeps', 9), ('extrusion midmesh', None)]
    if kind != 'sheet':
        methods = [methods[2], methods[1], methods[0]]
    failures = []
    for index, (name, method) in enumerate(methods):
        if index:
            model.readfile(filename=str(checkpoint), load_cad_geometry_as_graphics=0)
        try:
            size = settings['element_size']
            elements = (extract_midmesh(solid, size) if method is None else
                        batch_mesh(extract_midsurface(solid, method), size))
            groups = map_thickness(solid, elements, settings['thickness_tolerance'])
            coverage = check_mesh_coverage(solid, elements, groups)
            log.info('Solid %s: extraction accepted using %s', solid, name)
            checkpoint.unlink()
            return elements, groups, coverage, name
        except (ValueError, RuntimeError) as error:
            failures.append(f'{name}: {error}')
            log.warning('Solid %s: %s failed validation: %s', solid, name, error)
    raise ValueError(f'Solid {solid}: all extraction methods failed. ' + '\n'.join(failures))
