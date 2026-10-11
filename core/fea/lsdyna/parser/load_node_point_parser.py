from types import SimpleNamespace
from core.fea.parser import Parser
from core.fea.validation import required_id
from .card_fields import fields, number


class LoadNodePointParser(Parser):
    is_set = False

    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line):
        raw = fields(line)
        values = [number(v, self.dataframe, integer=i != 3, default=1 if i == 3 else 0)
                  for i, v in enumerate(raw)]
        required_id(raw[0], 'NID/NSID', self.dataframe)
        required_id(raw[2], 'LCID', self.dataframe)
        record = SimpleNamespace(**dict(zip(('target', 'dof', 'lcid', 'sf', 'cid', 'm1', 'm2', 'm3'), values)),
                                 is_set=self.is_set, source_context=self.source_context)
        store = self.dataframe.storge['load_node']
        store[len(store) + 1] = record
        self.line_number += 1
