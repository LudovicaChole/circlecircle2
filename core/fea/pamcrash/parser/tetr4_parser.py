from core.fea.parser import Parser
from core.fea.model.lsdyna.element_solid import ElementSolid
from core.fea.mesh_data import insert
from .card_fields import identifier


class Tetr4Parser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        eid, pid, *nodes = [identifier(line_raw[i:i+8]) for i in range(8, 56, 8)]
        nodes += [nodes[-1]]*4
        insert(self.dataframe.element_solid, ElementSolid(uid=eid, pid=pid,
               **{f'n{i+1}': n for i,n in enumerate(nodes)}))
