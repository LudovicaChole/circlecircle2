from core.fea.translator import Translator
from .analysis_data import is_explicit, period, curve_points, motion_dof, rigid_dofs, velocity_field


class StepTranslator(Translator):
    """Static by default; explicit for initial velocity or rigid motion."""
    def __init__(self):
        super().__init__()
        self.initial_increment = 0.01
        self.time_period = 1.0
        self.minimum_increment = 1e-8
        self.maximum_increment = 0.1
        self.maximum_increments = 1000

    def translate(self, version, history_include=None):
        if version != '6.14':
            raise ValueError(f'ABAQUS StepTranslator: unsupported version {version}')
        df = self.dataframe
        end = period(df, self.time_period)
        dynamic = is_explicit(df)
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
            if getattr(motion,'birth',0) != 0 or getattr(motion,'death',1e28) < end:
                raise ValueError('Rigid motion BIRTH/DEATH requires multiple analysis steps')
            points = curve_points(df.define_curve[motion.lcid])
            sf = getattr(motion,'sf',1.0)
            if dof in rigid_dofs(material) and any(sf*y != 0 for _,y in points):
                raise ValueError(f'Part {motion.typeid}: MAT20 constraint conflicts with prescribed DOF {dof}')
            amplitude = f'dyna_motion_{motion.uid}'
            lines.append(f'*AMPLITUDE, NAME={amplitude}, TIME=TOTAL TIME\n')
            lines += [f'{x:.12g}, {y:.12g}\n' for x,y in points]
            kind = {0:'VELOCITY',1:'ACCELERATION',2:'DISPLACEMENT'}[vad]
            motions += [f'** PART {motion.typeid}, MAT20 {part.mid}, LCID {motion.lcid}, source DOF {motion.dof}\n',
                        f'*BOUNDARY, TYPE={kind}, AMPLITUDE={amplitude}\n',
                        f'{ref}, {dof}, {dof}, {sf:.12g}\n']
        lines.append('*STEP, NAME=DefaultStep, NLGEOM=YES' + ('\n' if dynamic else f', INC={self.maximum_increments}\n'))
        if dynamic:
            lines += ['*DYNAMIC, EXPLICIT\n', f', {end:.12g}\n']
        else:
            lines += ['*STATIC\n', f'{min(self.initial_increment,end)}, {end}, {self.minimum_increment}, {min(self.maximum_increment,end)}\n']
        lines.extend(motions)
        lines.extend(df.output_storge.get('*STEP_CONTACT', []))
        lines.extend(df.output_history_node if dynamic else
                     [line.replace('U, V, A, RF', 'U, RF') for line in df.output_history_node])
        lines.append('*END STEP\n')
        return lines
