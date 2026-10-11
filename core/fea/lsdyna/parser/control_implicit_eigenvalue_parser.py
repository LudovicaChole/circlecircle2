from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class ControlImplicitEigenvalueParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line):
        raw = fields(line)
        if not self.line_number:
            names = ('neig', 'center', 'lflag', 'lftend', 'rflag', 'rhtend', 'eigmth', 'shfscl')
            values = {name: number(value, self.dataframe, integer=i in (0, 2, 4, 6))
                      for i, (name, value) in enumerate(zip(names, raw))}
            record = SimpleNamespace(**values, source_context=self.source_context, options=[])
            self.dataframe.storge['implicit_eigenvalue'][1] = record
        else:
            self.dataframe.storge['implicit_eigenvalue'][1].options.append(
                [number(value, self.dataframe) for value in raw])
        self.line_number += 1
