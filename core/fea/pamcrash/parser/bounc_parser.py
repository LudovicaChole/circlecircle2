from core.fea.parser import Parser
from core.fea.model.lsdyna.boundary_spc_node import BoundarySpcNode
from .card_fields import value
from .node_selection import nodes


class BouncParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        self.temp.append(line_raw.rstrip())

    def finish(self):
        if not self.temp:
            return
        head = self.temp[0]
        nid = value(head[8:16], integer=True)
        if value(head[24:32], integer=True) or value(head[32:40], integer=True):
            raise ValueError('BOUNC: local frames and sensor activation require explicit conversion')
        mask = head[18:24].replace(' ', '0').ljust(6,'0')
        if len(mask) != 6 or set(mask)-{'0','1'}:
            raise ValueError(f'BOUNC: invalid DOFCOD {mask}')
        selected = [nid] if nid else nodes(self.temp[1:], self.dataframe)
        if not selected:
            raise ValueError('BOUNC: empty node selection')
        store = self.dataframe.storge['boundary_spc_node']
        for nid in selected:
            if nid not in self.dataframe.node:
                raise ValueError(f'BOUNC: missing node {nid}')
            dofs = {i+1 for i,v in enumerate(mask) if v=='1'}
            if nid in store:
                dofs.update(store[nid].dofs)
            store[nid] = BoundarySpcNode(nid, tuple(sorted(dofs)))
        self.reset()
