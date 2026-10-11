from core.fea.translator import Translator
from .card_fields import card
from core.fea.abaqus.translator.analysis_data import curve_points


class MotionTranslator(Translator):
    def translate(self, version):
        df = self.dataframe
        lines = []
        used = set(df.define_curve) | set(df.define_table)
        for m in df.storge['prescribed_motion_node'].values():
            cid = max(used,default=0)+1
            used.add(cid)
            from core.fea.model.lsdyna.define_curve import DefineCurve
            original = df.define_curve[m.lcid]
            physical = curve_points(original)
            c = DefineCurve(uid=cid,sfa=1,sfo=1)
            c.a1,c.o1 = map(list,zip(*physical))
            df.define_curve[cid] = c
            lines += ['*DEFINE_CURVE\n',card((cid,0,1,1,0,0)),
                      *[card((t,y),20) for t,y in curve_points(df.define_curve[m.lcid])],
                      '*BOUNDARY_PRESCRIBED_MOTION_NODE\n',
                      card((m.nid,{1:1,2:2,3:3,4:5,5:6,6:7}[m.dof],m.vad,cid,m.sf,0,m.death,m.birth))]
        for m in df.boundary_prescribed_motion_rigid.values():
            cid = max(used,default=0)+1
            used.add(cid)
            from core.fea.model.lsdyna.define_curve import DefineCurve
            physical = curve_points(df.define_curve[m.lcid])
            curve = DefineCurve(uid=cid,sfa=1,sfo=1)
            curve.a1,curve.o1 = map(list,zip(*physical))
            df.define_curve[cid] = curve
            lines += ['*DEFINE_CURVE\n',card((cid,0,1,1,0,0)),
                      *[card((t,y),20) for t,y in physical],
                      '*BOUNDARY_PRESCRIBED_MOTION_RIGID\n',
                      card((m.typeid,m.dof,getattr(m,'vad',0),cid,getattr(m,'sf',1),getattr(m,'vid',0),
                            getattr(m,'death',1e28),getattr(m,'birth',0)))]
        df.output_storge['*NODE_MOTION'] = lines
        # InteractionTranslator owns rigid body cards to avoid overlapping constraints.
        df.output_storge['*NODAL_RIGID_BODY'] = []
        masses = []
        for m in df.storge['element_mass'].values():
            masses += ['*ELEMENT_MASS\n',card((m.uid,m.nid),8).rstrip('\n')+card((m.mass,),16).rstrip('\n')+card((getattr(m,'pid',0),),8)]
        df.output_storge['*ELEMENT_MASS'] = masses
