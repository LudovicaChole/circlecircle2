"""Beam topology, orientation and releases retained independently of solids."""
from types import SimpleNamespace
from core.fea.parser import Parser
from core.fea.mesh_data import insert
from core.fea.validation import required_id
from .card_fields import fields, number


class ElementBeamParser(Parser):
    def __init__(self, orientation=False):
        super().__init__()
        self.orientation = orientation
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line):
        if not self.temp:
            raw = fields(line, (8,) * 10)
            values = [number(v, self.dataframe, integer=True, default=2 if i == 9 else 0)
                      for i, v in enumerate(raw)]
            for i, label in enumerate(('EID', 'PID', 'N1', 'N2')):
                required_id(raw[i], label, self.dataframe)
            record = SimpleNamespace(**dict(zip(
                ('uid', 'pid', 'n1', 'n2', 'n3', 'rt1', 'rr1', 'rt2', 'rr2', 'local'), values)),
                vector=None, format='beam', source_context=self.source_context)
            if self.orientation:
                self.temp.append(record)
            else:
                insert(self.dataframe.storge['element_beam'], record)
        else:
            record = self.temp.pop()
            record.vector = tuple(number(v, self.dataframe) for v in fields(line)[:3])
            insert(self.dataframe.storge['element_beam'], record)
        self.line_number += 1
