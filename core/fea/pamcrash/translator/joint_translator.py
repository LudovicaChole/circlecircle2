"""Revolute constraints as PAM general KJOIN with one released axial rotation."""
from core.fea.translator import Translator
from core.fea.joint_geometry import basis
from core.fea.conversion_notes import unconverted
from .selection import field


class JointTranslator(Translator):
    def translate(self, version):
        df, lines = self.dataframe, []
        pid = max(df.part,default=0)+len(df.storge['surface_ties'])+1
        eid = max(set(df.element_shell)|set(df.element_solid)|set(df.storge['element_beam']),default=0)+1
        for index,joint in enumerate(df.storge['joints'].values()):
            axis, second = basis(df,joint)
            fid = index+1
            # IAXIS=0 supplies U and V; r=U is the released revolute axis.
            lines += ['FRAME / '+field(fid)+field(0)+field(0)+'\n',f'NAME joint_axis_{joint.uid}\n',
                      ' '*8+''.join(field(v,16) for v in axis)+'\n',
                      ' '*8+''.join(field(v,16) for v in second)+'\n',
                      'PART  / '+field(pid+index)+field('KJOIN')+' '*32+'\n',f'NAME joint_{joint.uid}\n',
                      '       0.0       1.0\n',' '*30+'\n','\n','END_PART\n',
                      'KJOIN / '+''.join(field(v) for v in (eid+index,pid+index,'GENERAL',joint.nodes[0],joint.nodes[1],fid,fid,joint.rps))+'\n',
                      ' '*10+'111011\n']
            if joint.damp not in (0,1):
                unconverted(f'Joint {joint.uid}: LS-DYNA damping scaling is archived; KJOIN damping is not directly equivalent',joint)
        for prop in df.storge['joint_stiffness'].values():
            unconverted(f'Joint stiffness {prop.uid}: PAM flexion-torsion material law is archived; kinematic revolute constraint is mapped',prop)
        df.output_storge['KJOIN'] = lines
