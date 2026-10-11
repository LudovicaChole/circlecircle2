from core.fea.parser import Parser
from core.fea.model.lsdyna.node import Node
from core.fea.mesh_data import insert
from .card_fields import identifier, value


class NodeParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        nid = identifier(line_raw[8:16])
        xyz = [value(line_raw[i:i+16]) for i in (16, 32, 48)]
        insert(self.dataframe.node, Node(uid=nid, x=xyz[0], y=xyz[1], z=xyz[2]))
