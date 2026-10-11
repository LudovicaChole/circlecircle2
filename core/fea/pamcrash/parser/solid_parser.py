from core.fea.parser import Parser
from core.fea.model.lsdyna.element_solid import ElementSolid
from core.fea.mesh_data import insert
from .card_fields import identifier


class SolidParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        if self.line_number == 0:
            self.temp = [identifier(line_raw[8:16]), identifier(line_raw[16:24])]
            self.line_number = 1
            return
        nodes = [identifier(line_raw[i:i+8]) for i in range(16, 80, 8)]
        element = ElementSolid(uid=self.temp[0], pid=self.temp[1],
                               **{f'n{i+1}': n for i,n in enumerate(nodes)})
        if element.format is None:
            raise ValueError('SOLID: unsupported degenerate connectivity')
        insert(self.dataframe.element_solid, element)
        self.reset()

    def finish(self):
        if self.line_number:
            raise ValueError('SOLID: missing connectivity card')
