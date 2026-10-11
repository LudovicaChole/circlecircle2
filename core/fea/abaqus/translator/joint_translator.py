"""Revolute rigid-body joints as oriented Abaqus HINGE connectors."""
from core.fea.translator import Translator
from core.fea.joint_geometry import basis
from core.fea.conversion_notes import unconverted
from .analysis_data import curve_points


class JointTranslator(Translator):
    def translate(self, version):
        df, lines = self.dataframe, []
        eid = max(set(df.element_shell)|set(df.element_solid)|set(df.storge['element_beam']),default=0)
        stiffness = {p.jid:p for p in df.storge['joint_stiffness'].values()}
        for joint in df.storge['joints'].values():
            axis, second = basis(df,joint)
            eid += 1
            name = f'CC2_JOINT_{joint.uid}'
            prop = stiffness.get(joint.uid)
            behavior = []
            if prop:
                refs = prop.rows[1]
                # A revolute joint has only its axial torsion rotation available.
                if refs[2]:
                    cid = int(refs[2])
                    if cid not in df.define_curve:
                        raise ValueError(f'Joint {joint.uid}: missing torsion curve {cid}')
                    behavior += ['*CONNECTOR ELASTICITY, COMPONENT=4, NONLINEAR\n']
                    behavior += [f'{moment}, {rotation}\n' for rotation,moment in curve_points(df.define_curve[cid])]
                if any(refs[i] for i in (0,1,3,4,5)) or any(prop.rows[2][i] for i in (1,3)) or any(prop.rows[3]):
                    unconverted(f'Joint stiffness {prop.uid}: coupled damping/friction/stops are archived; only axial torque curve is mapped',prop)
            lines += [f'*ELEMENT, TYPE=CONN3D2, ELSET={name}\n', f'{eid}, {joint.nodes[0]}, {joint.nodes[1]}\n',
                      f'*ORIENTATION, NAME={name}_AXIS\n', ', '.join(str(v) for v in (*axis,*second))+'\n']
            if behavior:
                lines += [f'*CONNECTOR BEHAVIOR, NAME={name}_LAW\n', *behavior]
            parameter = f', BEHAVIOR={name}_LAW' if behavior else ''
            lines += [f'*CONNECTOR SECTION, ELSET={name}{parameter}\n','HINGE\n',f'{name}_AXIS, {name}_AXIS\n']
            if joint.rps != 1 or joint.damp not in (0,1):
                unconverted(f'Joint {joint.uid}: LS-DYNA penalty/damping control is archived; Abaqus HINGE enforces kinematic constraints',joint)
        for prop in df.storge['joint_stiffness'].values():
            if prop.jid not in df.storge['joints']:
                unconverted(f'Joint stiffness {prop.uid}: no supported revolute joint JID {prop.jid}; archived',prop)
        df.output_storge['*JOINTS'] = lines
