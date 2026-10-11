from core.fea.parser import Parser
from core.fea.model.lsdyna.boundary_spc_node import BoundarySpcNode
from .card_fields import fields, number


class BoundarySpcNodeParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0','13.0','16.0'), self._parse)

    def _parse(self, line_raw):
        nid,cid,*mask = [number(v,self.dataframe,integer=True) for v in fields(line_raw)]
        if cid or set(mask)-{0,1} or nid <= 0:
            raise ValueError('BOUNDARY_SPC_NODE: requires global frame and binary DOFs')
        store = self.dataframe.storge['boundary_spc_node']
        dofs = {i+1 for i,v in enumerate(mask) if v}
        if nid in store:
            dofs.update(store[nid].dofs)
        store[nid] = BoundarySpcNode(nid,tuple(sorted(dofs)))
