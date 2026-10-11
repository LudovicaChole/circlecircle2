from core.fea.parser import Parser
from core.fea.model.lsdyna.initial_velocity_node import InitialVelocityNode
from .card_fields import value
from .node_selection import nodes


class InvelParser(Parser):
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
        if value(head[64:72], integer=True) or value(head[72:80], integer=True):
            raise ValueError('INVEL: local frame/rigid-body motion requires explicit conversion')
        components = tuple(value(head[i:i+8]) for i in range(16,64,8))
        selected = [nid] if nid else nodes(self.temp[1:], self.dataframe)
        if not selected:
            raise ValueError('INVEL: empty node selection')
        store = self.dataframe.storge['initial_velocity_node']
        for nid in selected:
            if nid not in self.dataframe.node:
                raise ValueError(f'INVEL: missing node {nid}')
            if nid in store and store[nid].components != components:
                raise ValueError(f'INVEL: conflicting velocities at node {nid}')
            store[nid] = InitialVelocityNode(nid, components)
        self.reset()
