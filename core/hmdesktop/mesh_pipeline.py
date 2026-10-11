"""Batch orchestrator only. Each HyperMesh operation lives in its own module."""
import json
import logging
from pathlib import Path
import traceback


def run_job(config_path):
    import hm
    from .tcl_bridge import run, ids, value, quote
    from .load_geometry import load_geometry
    from .validate_geometry import validate_geometry
    from .classify_geometry import classify_geometry
    from .mesh_solid import mesh_solid
    from .assign_material import Materials
    from .check_mesh_quality import check_mesh_quality
    from .mesh_welds import mesh_welds
    from .component_names import component_name
    from .mesh_shell_surfaces import mesh_shell_surfaces
    from .job_reports import MeshLogFormatter
    from .assign_part_controls import assign_part_controls
    config = json.loads(Path(config_path).read_text(encoding='utf-8'))
    directory, settings = Path(config['job']), config['settings']
    log = logging.getLogger('hwx_mesh')
    log.setLevel(logging.INFO)
    handler = logging.FileHandler(directory/'hwx_mesh.log', encoding='utf-8')
    handler.setFormatter(MeshLogFormatter('%(asctime)s  [%(levelname)-7s]\n  %(message)s', '%Y-%m-%d %H:%M:%S'))
    log.addHandler(handler)
    result = dict(success=False, output=config['output'], bodies=[])
    model = hm.Model()
    try:
        log.info('Load %s; units kg/mm/ms; mesh size %s mm', config['source'], settings['element_size'])
        load_geometry(model, config['source'])
        solids, surfaces, seams = validate_geometry()
        result['seam_lines'] = seams
        log.info('Geometry: %d solids, %d surfaces, %d standalone seam lines', len(solids), len(surfaces), len(seams))
        from .weld_proximity import find_weld_pairs
        weld_pairs = find_weld_pairs(solids, log)
        owned = set()
        for solid in solids:
            owned.update(int(v) for v in run(f'hm_getsurfacesfromsolid {solid}').split())
        orphan_surfaces = sorted(set(surfaces)-owned)
        if orphan_surfaces and not settings.get('surface_thickness'):
            names = sorted({value('comps', int(value('surfs', sid, 'collector.id')), 'name') for sid in orphan_surfaces})
            raise ValueError(f'Surface-only geometry has no measurable solid thickness: {names}, '
                             f'surfaces {orphan_surfaces}. Specify surface_thickness in mm before meshing.')
        catalog = Materials(model, Path(config['catalog']), directory, settings, log)
        components = {}
        for solid in solids:
            source_comp = int(value('solids', solid, 'collector.id'))
            name = value('comps', source_comp, 'name')
            tag = catalog.suffix(name)
            kind, bounds = classify_geometry(solid, settings['thickness_tolerance'])
            log.info('Solid %s, component %s: thickness classification %s, bounds %s', solid, name, kind, bounds)
            elements, groups, coverage, route = mesh_solid(model, solid, kind, directory, settings, log)
            measured_bounds = [min(groups.values()), max(groups.values())]
            measured_kind = ('variable' if measured_bounds[1]-measured_bounds[0] >
                             settings['thickness_tolerance'] else 'sheet')
            log.info('Solid %s: mapped thickness %s, coverage volume difference %.2f%%',
                     solid, measured_bounds, 100*coverage['relative_error'])
            for component, thickness in groups.items():
                catalog.assign(component, tag)
                label = component_name(name, tag, thickness)
                run(f'*setvalue comps id={component} name={quote(label)}')
                components[component] = dict(tag=tag, thickness=thickness, name=label, solid=solid)
            result['bodies'].append(dict(solid=solid, source_component=source_comp,
                                         classification=measured_kind, extraction_route=route,
                                         bounds=measured_bounds, coverage=coverage,
                                         element_count=len(elements), components=groups))
        if orphan_surfaces:
            components.update(mesh_shell_surfaces(orphan_surfaces, catalog, directory, settings, log))
        check_mesh_quality(ids('elems'), directory)
        result['welding'] = mesh_welds(seams, components, catalog, settings, log, weld_pairs, directory)
        result['part_controls'] = assign_part_controls(model, log)
        model.writefile(filename=config['output'], do_not_write_facets=1)
        result.update(success=True, elements=len(ids('elems')), components=components)
        log.info('Completed: %s', config['output'])
    except Exception as error:
        result['error'] = str(error)
        result['traceback'] = traceback.format_exc()
        log.exception('hwx_mesh failed')
        with (directory/'quality.txt').open('a', encoding='utf-8') as report:
            report.write('\nJOB VALIDATION FAILED\n'+str(error)+'\n'
                         'Any preceding quality table is not approval of the final model.\n')
        try:
            model.writefile(filename=str(directory/'failed_debug.hm'), do_not_write_facets=1)
        except Exception:
            log.exception('Unable to save diagnostic model')
    finally:
        temporary = directory/'result.tmp'
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(directory/'result.json')
        handler.close()
        log.removeHandler(handler)
        run('*quit 1')
