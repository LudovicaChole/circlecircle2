from core.fea.translator import Translator
from .selection import ids, field, selection


class MtocoTranslator(Translator):
    def translate(self, version):
        lines = []
        for body in self.dataframe.constrained_nodal_rigid_body.values():
            if body.cid or body.drflag or body.rrflag:
                raise ValueError(f'Rigid body {body.uid}: local/released constraints require manual MTOCO mapping')
            nodes = ids(self.dataframe,self.dataframe.set_node_list[body.sid].ids)
            reference = body.pnode or nodes[0]
            slaves = [nid for nid in nodes if nid != reference]
            if reference not in self.dataframe.node or any(n not in self.dataframe.node for n in slaves):
                raise ValueError(f'Rigid body {body.uid}: missing nodes')
            lines.extend(['$#         IDMTO  IDNODi  DOFCOD   IFRA1   ITMTO\n',
                          'MTOCO / '+''.join(field(v) for v in (body.pid,reference,111111,0,0))+'\n',
                          f'NAME {body.name}\n'])
            lines.extend(selection('NOD',slaves))
        self.dataframe.output_storge['MTOCO'] = lines
