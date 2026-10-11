import json
from core.fea.translator import Translator
from .analysis_data import is_explicit, period, curve_points, motion_dof, rigid_dofs, velocity_field


class StepTranslator(Translator):
    """Convert mechanical loading to Abaqus/Standard static displacement."""
    def __init__(self):
        super().__init__()
        self.initial_increment = 0.01
        self.time_period = 1.0
        self.minimum_increment = 1e-8
        self.maximum_increment = 0.1
        self.maximum_increments = 1000

    def translate(self, version, history_include=None):
        if version not in ('6.14', '2024'):
            raise ValueError(f'ABAQUS StepTranslator: unsupported version {version}')
        df = self.dataframe
        if '*THERMAL_STEP' in df.output_storge:
            return df.output_storge['*THERMAL_STEP']
        if df.storge['implicit_eigenvalue']:
            eigen = df.storge['implicit_eigenvalue'][1]
            if eigen.neig <= 0 or eigen.center or eigen.lflag or eigen.rflag:
                raise ValueError('Eigenvalue curve/shift/frequency-window mapping is not implemented')
            if df.storge['load_node'] or is_explicit(df):
                raise ValueError('Preloaded/dynamic eigenvalue analysis needs a preceding analysis step')
            from core.fea.conversion_notes import unconverted
            unconverted('Eigenvalue count mapped to Abaqus Lanczos; LS-DYNA eigensolver '
                        'and eigenvector-output controls use Abaqus defaults', eigen)
            return ['*STEP, NAME=Eigenmodes, PERTURBATION\n', '*FREQUENCY, EIGENSOLVER=LANCZOS\n',
                    f'{eigen.neig}\n', '*OUTPUT, FIELD\n', '*NODE OUTPUT\n', 'U\n', '*END STEP\n']
        end = period(df, self.time_period)
        lines = ['** Time, mass, velocity and energy use the source consistent unit system.\n']
        velocities = velocity_field(df)
        if velocities:
            masses = [m for m in df.storge.get('element_mass', {}).values() if m.nid in velocities]
            energy = sum(0.5*m.mass*sum(v*v for v in velocities[m.nid][:3]) for m in masses)
            lines += [f'** INITIAL KINETIC ENERGY (selected ELEMENT_MASS only) = {energy:.12g}\n',
                      f'** Selected point mass = {sum(m.mass for m in masses):.12g}; elements = {len(masses)}.\n',
                      '** This subtotal excludes shell/solid density mass and rotary inertia.\n']
        motions = []
        occupied = set()
        for motion in df.boundary_prescribed_motion_rigid.values():
            part = df.part[motion.typeid]
            material = df.material[part.mid]
            if material.tag != 'rigid':
                raise ValueError(f'Prescribed rigid motion part {motion.typeid} does not use MAT20')
            dof = motion_dof(motion)
            ref = df.storge_rigid_part_reference_node[motion.typeid]
            if (ref,dof) in occupied:
                raise ValueError(f'Duplicate prescribed rigid motion for part {motion.typeid}, DOF {dof}')
            occupied.add((ref,dof))
            vad = getattr(motion,'vad',0)
            if vad not in (0,1,2):
                raise ValueError(f'Unsupported rigid motion VAD={vad}')
            source_points = curve_points(df.define_curve[motion.lcid])
            points = displacement_points(source_points, vad, end, getattr(motion, 'birth', 0), getattr(motion, 'death', 1e28))
            sf = getattr(motion,'sf',1.0)
            if dof in rigid_dofs(material) and any(sf*y != 0 for _,y in points):
                # Modify the initial boundary in the step while preserving
                # its model-data constraint for a comment-free round trip.
                notice = (f'Part {motion.typeid}: MAT20 also constrains DOF {dof}; '
                          'Abaqus conversion uses prescribed motion on this DOF '
                          'and retains the initial MAT20 constraint mask in model data')
                from utilities.logger import logger
                logger.warning(notice, source=motion)
                lines.append('** RIGID MOTION PRECEDENCE: ' + notice + '\n')
            amplitude = f'dyna_motion_{motion.uid}'
            lines.append(f'*AMPLITUDE, NAME={amplitude}, TIME=TOTAL TIME\n')
            lines += [f'{x:.12g}, {y:.12g}\n' for x,y in points]
            lines.append('** CIRCLECIRCLE2_MOTION ' + json.dumps([ref,dof,vad,sf,source_points,getattr(motion,'birth',0),getattr(motion,'death',1e28)], separators=(',', ':')) + '\n')
            kind = 'DISPLACEMENT'
            motions += [f'** PART {motion.typeid}, MAT20 {part.mid}, LCID {motion.lcid}, source DOF {motion.dof}\n',
                        f'*BOUNDARY, OP=MOD, TYPE={kind}, AMPLITUDE={amplitude}\n',
                        f'{ref}, {dof}, {dof}, {sf:.12g}\n']
        for motion in df.storge['prescribed_motion_node'].values():
            ref, dof = motion.nid, motion.dof
            if (ref,dof) in occupied:
                raise ValueError(f'Duplicate prescribed motion at node {ref}, DOF {dof}')
            occupied.add((ref,dof))
            source = curve_points(df.define_curve[motion.lcid])
            points = displacement_points(source, motion.vad, end, motion.birth, motion.death)
            name = f'source_node_motion_{motion.uid}'
            lines += [f'*AMPLITUDE, NAME={name}, TIME=TOTAL TIME\n']
            lines += [f'{t:.12g}, {u:.12g}\n' for t,u in points]
            lines.append('** CIRCLECIRCLE2_MOTION ' + json.dumps([ref,dof,motion.vad,motion.sf,source,motion.birth,motion.death], separators=(',', ':')) + '\n')
            motions += [f'*BOUNDARY, TYPE=DISPLACEMENT, AMPLITUDE={name}\n', f'{ref}, {dof}, {dof}, {motion.sf:.12g}\n']
        rotational_nodes = set(df.storge_rigid_part_goc_xyz)
        for element in df.element_shell.values():
            rotational_nodes.update(getattr(element,f'n{i}',0) for i in range(1,5))
        rotational_nodes.update(b.pnode for b in df.constrained_nodal_rigid_body.values())
        for nid, components in sorted(velocities.items()):
            fixed = df.storge['boundary_spc_node'].get(nid)
            for dof, value in enumerate(components, 1):
                if dof > 3 and nid not in rotational_nodes:
                    continue
                if fixed and dof in fixed.dofs:
                    continue
                if value and (nid, dof) not in occupied:
                    motions += [f'** Source initial velocity {value:.12g}; displacement = velocity * duration.\n',
                                '*BOUNDARY, TYPE=DISPLACEMENT\n', f'{nid}, {dof}, {dof}, {value*end:.12g}\n']
        lines.append(f'** CIRCLECIRCLE2_DURATION {end:.12g}\n')
        from .nodal_loads import nodal_loads
        amplitudes, forces = nodal_loads(df)
        lines.extend(amplitudes)
        lines.append(f'*STEP, NAME=DefaultStep, NLGEOM=YES, INC={self.maximum_increments}\n')
        lines += ['*STATIC\n', f'{self.initial_increment*end}, {end}, {self.minimum_increment*end}, {self.maximum_increment*end}\n']
        lines.extend(motions)
        lines.extend(forces)
        lines.extend(df.output_storge.get('*STEP_CONTACT', []))
        lines.extend([line.replace('U, V, A, RF', 'U, RF') for line in df.output_history_node])
        lines.extend(['*OUTPUT, FIELD\n', '*NODE OUTPUT\n', 'U, RF\n', '*ELEMENT OUTPUT\n', 'S, LE, PE, PEEQ, ENER\n', '*OUTPUT, HISTORY\n', '*ENERGY OUTPUT\n', 'ALLIE, ALLSE, ALLPD, ALLWK\n'])
        lines.append('*END STEP\n')
        return lines


def displacement_points(points, vad, end, birth=0.0, death=1e28):
    """Integrate linear velocity/acceleration exactly at curve knots.

    Intermediate samples approximate the integrated polynomial amplitude;
    endpoints and the total displacement are exact.
    """
    from bisect import bisect_right
    def value(t):
        i = bisect_right([x for x,y in points], t)-1
        if i < 0:
            return points[0][1]
        if i >= len(points)-1:
            return points[-1][1]
        x,y = points[i]; x1,y1 = points[i+1]
        return y + (y1-y)*(t-x)/(x1-x)
    knots = sorted({0.0, float(end), *[x for x,y in points if 0 < x < end],
                    *[x for x in (birth,death) if 0 < x < end]})
    result = [(0.0, value(0) if vad == 2 and birth <= 0 else 0.0)]
    displacement = velocity = 0.0
    for a,b in zip(knots,knots[1:]):
        active = a >= birth and a < death
        y0,y1 = (value(a), value(b)) if active else (0.0,0.0)
        dt = b-a; slope = (y1-y0)/dt
        for j in range(1,17):
            h = dt*j/16
            if vad == 0:
                u = displacement + y0*h + slope*h*h/2
            elif vad == 1:
                u = displacement + velocity*h + y0*h*h/2 + slope*h*h*h/6
            else:
                u = value(a+h) if active else displacement
            result.append((a+h,u))
        displacement = result[-1][1]
        if vad == 1:
            velocity += (y0+y1)*dt/2
    return result
