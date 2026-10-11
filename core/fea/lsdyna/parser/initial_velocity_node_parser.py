from core.fea.parser import Parser
from core.fea.model.lsdyna.initial_velocity_node import InitialVelocityNode
from .card_fields import fields, number


class InitialVelocityNodeParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0','13.0','16.0'), self._parse)

    def _parse(self, line_raw):
        raw = fields(line_raw)
        nid = number(raw[0],self.dataframe,integer=True)
        if nid <= 0 or number(raw[7],self.dataframe,integer=True):
            raise ValueError('INITIAL_VELOCITY_NODE: positive NID and global coordinates required')
        components = tuple(number(v,self.dataframe) for v in raw[1:7])
        store = self.dataframe.storge['initial_velocity_node']
        if nid in store and store[nid].components != components:
            raise ValueError(f'Conflicting initial velocity for node {nid}')
        store[nid] = InitialVelocityNode(nid,components)
