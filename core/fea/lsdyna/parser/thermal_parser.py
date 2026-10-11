"""Common storage for documented LS-DYNA thermal cards; no structural aliases."""
from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class ThermalParser(Parser):
    keyword = ''
    names = ()
    integers = ()
    defaults = {}
    cards = 1
    title = False

    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line):
        if self.title and not self.line_number:
            self.line_number += 1
            return
        index = len(self.temp)
        names = self.names[index]
        values = {name: number(value, self.dataframe, integer=name in self.integers,
                               default=self.defaults.get(name, 0))
                  for name, value in zip(names, fields(line)) if name != '-'}
        if not index:
            self.record_source = self.source_context
        self.temp.append(values)
        self.line_number += 1
        if len(self.temp) == self.cards:
            merged = {}
            for card in self.temp:
                merged.update(card)
            record = SimpleNamespace(keyword=self.keyword, source_context=self.record_source, **merged)
            store = self.dataframe.storge['thermal']
            store[len(store) + 1] = record
            self.temp.clear()
