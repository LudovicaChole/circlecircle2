"""NN-gated towing assembly appended to the translated Abaqus model."""
import numpy as np
from dataclasses import replace
from utilities.logger import logger
from utilities.towing_settings import load, model_path
from core.hmdesktop.towing_geometry import fit_cylinder, exterior, cylindrical_faces, make_insert
from core.fea.abaqus.translator.contact_surface import ContactSurface


def append_towing(df, settings=None):
    options = settings if settings is not None else load()
    if not options['enabled']:
        return 0
    if not model_path('hook').is_file():
        logger.warning('No towing hook neural-network model is available. Enter -nn and train Towing Hook NN. No towing solid was generated.')
        return 0
    from core.fea.abaqus.translator.thermal_translator import thermal_mode
    if thermal_mode(df):
        logger.warning('Automatic towing solids are supported for structural conversions only; thermal assembly skipped.')
        return 0
    from core.nn.towing_pointnet import Predictor
    predictor = Predictor('hook')
    template_predictor = None
    if options['template']:
        if not model_path('towing').is_file():
            logger.warning('No Towing Shape NN model is available. The selected solid towing template was not assembled.')
            return 0
        template_predictor = Predictor('towing')
    nid = max([*df.node, *df.storge_rigid_part_goc_xyz,
               *df.storge_rigid_part_reference_node.values()], default=0)+1
    eid = max([*df.element_shell, *df.element_solid, *df.storge['element_beam']], default=0)+1
    pending, count, recognized = [], 0, 0
    for pid, ids in sorted(df.storge_part_node_id.items()):
        if len(ids) < 12:
            continue
        points = np.array([df.node[n].xyz for n in sorted(ids)])
        probability = predictor.probability(points)
        if probability < predictor.threshold:
            continue
        recognized += 1
        try:
            hole = fit_cylinder(df,pid)
            shell_thickness = 0.0
            part = df.part[pid]
            section = df.section_shell.get(part.secid)
            if section is not None:
                if any(e.format not in ('s3','s4') for e in df.storge_part_element[pid]):
                    raise ValueError('Mixed shell/solid towing parts need separate sections.')
                shell_thickness = float(section.t1)
                if shell_thickness <= 0 or shell_thickness/2 >= hole.radius:
                    raise ValueError('Invalid shell thickness for towing bore.')
            # A shell cloud describes the midsurface; the physical bore is t/2 inward.
            insert_hole = replace(hole, radius=hole.radius-shell_thickness/2)
            name = f'C2_TOWING_{pid}'
            # Do not collide with source names even when IDs are already distinct.
            while any(name in ''.join(lines) for lines in df.output_storge.values()):
                name += '_NEW'
            if options['template']:
                from core.hmdesktop.towing_template import read_template, copy_template
                template = read_template(options['template'])
                lines, insert_faces, next_nid, next_eid, low, high = copy_template(
                    template, insert_hole, options['length'], nid, eid, name, template_predictor)
            else:
                material = df.material[df.part[pid].mid].name
                lines, insert_faces, next_nid, next_eid, low, high = make_insert(
                    insert_hole, options['length'], nid, eid, name, material)
                logger.info(f'Generated towing part {pid} uses host material {material}.')
            hole_faces = cylindrical_faces(df, exterior(df,pid), hole, low, high)
            if not hole_faces:
                raise ValueError('No complete hole wall faces lie within the overlap; increase L or refine the mesh.')
            lines += ContactSurface.write_surface(name+'_HOLE', hole_faces)
            lines += ContactSurface.write_surface(name+'_INSERT', insert_faces)
            tie_tolerance = hole.tolerance+shell_thickness/2
            # Keep source nodes as the main surface: they can already belong to
            # rigid couplings or boundary constraints. Only the new insert is secondary.
            lines.extend([f'*TIE, NAME={name}_TIE, TYPE=SURFACE TO SURFACE, ADJUST=NO, POSITION TOLERANCE={tie_tolerance:.12g}\n',
                          f'{name}_INSERT, {name}_HOLE\n'])
        except (ValueError, KeyError) as error:
            # A failed target must never leave half an insert in the output.
            logger.warning(f'Towing part {pid} skipped: {error}')
            continue
        pending.extend(lines)
        nid, eid = next_nid, next_eid
        count += 1
        logger.info(f'Towing part {pid}: NN confidence {probability:.3f}; physical bore radius {insert_hole.radius:.6g}; signed L={options["length"]}; overlap {high-low:.6g}')
    if pending:
        df.output_storge['*C2_TOWING'] = pending
    logger.info(f'Automatic towing assembly: NN recognized {recognized} candidate parts; {count} inserts created.')
    return count
