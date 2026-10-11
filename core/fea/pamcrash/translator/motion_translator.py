from core.fea.translator import Translator
from .selection import field, selection
from core.fea.abaqus.translator.analysis_data import motion_dof


def rigid_motion_dofs(df, pid):
    """Prescribed motion replaces a fixed boundary on the same rigid DOF."""
    return {motion_dof(m) for m in df.boundary_prescribed_motion_rigid.values()
            if m.typeid == pid}


class MotionTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        lines = []
        motions = [(m, m.nid, m.dof, f'source_node_motion_{m.uid}')
                   for m in df.storge['prescribed_motion_node'].values()]
        for m in df.boundary_prescribed_motion_rigid.values():
            reference = df.storge_rigid_part_reference_node.get(m.typeid)
            if reference is None:
                raise ValueError(f'PAM rigid motion {m.uid}: missing rigid reference for part {m.typeid}')
            motions.append((m, reference, motion_dof(m), f'part_{m.typeid}_motion_{m.uid}'))
        used = set()
        grouped = {}
        for m, nid, dof, name in motions:
            if m.birth or m.death < 1e28:
                raise ValueError('PAM prescribed motion: BIRTH/DEATH needs sensor mapping')
            if getattr(m, 'vid', 0):
                raise ValueError('PAM prescribed motion: vector/offset motion is not mapped')
            if nid not in df.node or m.lcid not in df.define_curve:
                raise ValueError('PAM prescribed motion: missing node/curve')
            if dof not in range(1, 7) or m.vad not in (0, 1, 2):
                raise ValueError('PAM prescribed motion: unsupported DOF/VAD')
            if (nid, dof) in used:
                raise ValueError(f'PAM prescribed motion: duplicate node {nid}, DOF {dof}')
            used.add((nid, dof))
            grouped.setdefault((dof, m.vad, m.lcid, m.sf), []).append((nid, name))
        groups = []
        for index, ((dof, vad, lcid, sf), targets) in enumerate(grouped.items(), 1):
            rotational = dof > 3
            kind = ({0:'RVE3D',1:'RAC3D',2:'RAN3D'} if rotational else {0:'VEL3D',1:'ACC3D',2:'DIS3D'})[vad]
            axis = (dof-1)%3
            refs, scales = [0]*3, [1.0]*3
            refs[axis],scales[axis] = lcid,sf
            nid, name = targets[0] if len(targets) == 1 else (0, f'prescribed_motion_{index}')
            lines += [kind+' / '+''.join(field(v) for v in (nid,*refs,*scales,0,0))+'\n',
                      f'NAME {name}\n']
            if len(targets) > 1:
                # Selection is on the independent targets, never MTOCO dependents.
                group = f'converter_motion_targets_{index}'
                groups += [f"GROUP / '{group}'\n", *selection('NOD', [n for n, _ in targets])]
                lines += [f"        GRP '{group}'\n", '        END\n']
        df.output_storge['MOTION'] = lines
        df.output_storge['MOTION_GROUP'] = groups
