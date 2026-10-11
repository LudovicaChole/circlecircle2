from core.fea.parser import Parser
from core.fea.model.abaqus.node import Node
from core.fea.lsdyna.parser.card_fields import number
from core.fea.validation import required_id


class NodeParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'6.14': self._6p14, "2024": self._6p14}

    def _6p14(self, line_raw):
        values = [value.strip() for value in line_raw.split(',')]
        if len(values) > 4 and any(values[4:]):
            raise ValueError('NODE: expected NID, X, Y, Z')
        values = (values + ['']*4)[:4]
        uid = required_id(values[0], 'NID', self.dataframe)
        x, y, z = (number(value, self.dataframe) for value in values[1:])
        self.dataframe.node[uid] = Node(uid=uid, x=x, y=y, z=z)
