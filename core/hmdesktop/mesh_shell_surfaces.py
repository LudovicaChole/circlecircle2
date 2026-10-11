"""Mesh surface-only shell geometry only when the caller explicitly supplies thickness."""
from collections import defaultdict
from .tcl_bridge import ids, value, run, quote, mark
from .batch_mesh import batch_mesh
from .component_names import component_name


def mesh_shell_surfaces(surfaces, catalog, directory, settings, log):
    thickness = settings['surface_thickness']
    grouped = defaultdict(list)
    for sid in surfaces:
        grouped[int(value('surfs', sid, 'collector.id'))].append(sid)
    result = {}
    for source, faces in grouped.items():
        name = value('comps', source, 'name')
        tag = catalog.suffix(name)
        label = component_name(name, tag, thickness)
        section = max(ids('props'), default=0)+1
        section_file = directory/f'surface_section_{section}.k'
        section_file.write_text('*KEYWORD\n*SECTION_SHELL\n'
                                f'{section},2,0.833333,5\n'
                                f'{thickness},{thickness},{thickness},{thickness}\n*END\n',
                                encoding='utf-8')
        run(f'*feinputwithdata2 "#ls-dyna/dynakey" {quote(section_file)} 0 0 0 0 0 1 0 1 0')
        if section not in ids('props'):
            raise ValueError(f'Surface shell section {section} failed to import.')
        elements = batch_mesh(faces, settings['element_size'])
        run(f'*createentity comps cardimage=Part name={quote(label)}')
        component = int(run('hm_latestentityid comps'))
        run(f'*setvalue comps id={component} propertyid={{props {section}}}')
        mark('elems', elements)
        run(f'*movemark elems 1 {quote(label)}')
        catalog.assign(component, tag)
        actual = float(run(f'hm_getthickness comps {component}'))
        if abs(actual-thickness) > 1e-6:
            raise ValueError(f'Surface component {component}: incorrect shell thickness {actual}.')
        result[component] = dict(name=label, tag=tag, thickness=actual)
        log.info('Surface-only component %s: using explicitly supplied shell thickness %s mm, %s elements',
                 name, thickness, len(elements))
    return result
