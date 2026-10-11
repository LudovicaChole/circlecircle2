from core.fea.parser import Parser
from core.fea.model.lsdyna.boundary_spc_node import BoundarySpcNode
from .card_fields import fields, number


class BoundarySpcSetParser(Parser):
    def __init__(self, with_id=False):
        super().__init__()
        self.with_id = with_id
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line):
        if not self.with_id or self.line_number % 2:
            sid, cid, *mask = [number(v, self.dataframe, integer=True) for v in fields(line)]
            if cid or set(mask) - {0, 1}:
                raise ValueError('BOUNDARY_SPC_SET: requires global frame and binary DOFs')
            if sid not in self.dataframe.set_node_list:
                raise ValueError(f'BOUNDARY_SPC_SET: missing node set {sid}')
            store = self.dataframe.storge['boundary_spc_node']
            dofs = {i + 1 for i, value in enumerate(mask) if value}
            for raw in self.dataframe.set_node_list[sid].ids:
                nid = number(raw, self.dataframe, integer=True)
                if nid:
                    existing = set(store[nid].dofs) if nid in store else set()
                    store[nid] = BoundarySpcNode(nid, tuple(sorted(dofs | existing)))
        self.line_number += 1
