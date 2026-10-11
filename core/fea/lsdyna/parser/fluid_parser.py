"""Typed ICFD input preservation, separate from the structural mesh.

Reading these cards does not imply a target CFD formulation has been mapped.
"""
from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class FluidParser(Parser):
    keyword = ''
    rows = ()
    integers = ()
    widths = (10,) * 8
    repeat = False

    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line):
        index = min(self.line_number, len(self.rows)-1) if self.repeat else self.line_number
        if index >= len(self.rows):
            raise ValueError(f'{self.keyword}: extra cards have no documented layout')
        names = self.rows[index]
        values = {name: None if not value else number(value, self.dataframe, integer=name in self.integers)
                  for name, value in zip(names, fields(line, self.widths)) if name != '-'}
        store = self.dataframe.storge['fluid']
        if not self.line_number:
            self.temp = [SimpleNamespace(keyword=self.keyword, cards=[], raw_lines=[], sources=[],
                                         source_context=self.source_context)]
            store[len(store) + 1] = self.temp[0]
        self.temp[0].cards.append(values)
        self.temp[0].raw_lines.append(line)
        self.temp[0].sources.append(self.source_context)
        self.line_number += 1
