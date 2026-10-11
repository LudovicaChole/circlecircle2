"""Typed EM input preservation; target electromagnetic physics is not mapped."""
from dataclasses import dataclass, field
from core.fea.parser import Parser
from core.fea.lsdyna.em_cards import EM_SCHEMAS
from core.fea.lsdyna.parser.card_fields import fields, number


@dataclass
class ElectromagneticBlock:
    keyword: str
    source_context: str
    cards: list = field(default_factory=list)
    raw_lines: list = field(default_factory=list)
    sources: list = field(default_factory=list)


class ElectromagneticParser(Parser):
    keyword = ''

    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line_raw):
        schema = EM_SCHEMAS[self.keyword]
        names, types = schema.card(self.line_number)
        raw = fields(line_raw)
        values = {}
        for name, kind, value in zip(names, types, raw):
            if name == '-':
                continue
            try:
                values[name] = (None if not value else value if kind == 'A' and not value.startswith('&')
                                else number(value, self.dataframe, integer=kind == 'I'))
            except (ValueError, KeyError) as error:
                raise ValueError(f'{self.keyword} card {self.line_number+1} {name}: {error}') from error
        if self.line_number == 0:
            store = self.dataframe.storge['electromagnetic']
            record = ElectromagneticBlock('*'+self.keyword, getattr(self, 'source_context', ''))
            store[len(store)+1] = record
            self.temp = [record]
        record = self.temp[0]
        record.cards.append(values)
        record.raw_lines.append(line_raw)
        record.sources.append(getattr(self, 'source_context', ''))
        self.line_number += 1
