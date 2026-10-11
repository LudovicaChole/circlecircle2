"""LS-DYNA R13 SECTION_BEAM cards (10-column/free format)."""
from types import SimpleNamespace
from core.fea.parser import Parser
from core.fea.mesh_data import insert
from .card_fields import fields, number


class SectionBeamParser(Parser):
    def __init__(self, title=False):
        super().__init__()
        self.title = title
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self.read_card)

    def read_card(self, line):
        index = self.line_number - int(self.title)
        if index < 0:
            self.temp.append(line.strip())
        elif index == 0:
            raw = fields(line)
            values = [number(v, self.dataframe, integer=i in (0, 1, 4, 7),
                             default={1: 1, 2: 1, 3: 2}.get(i, 0)) for i, v in enumerate(raw)]
            names = ('uid', 'elform', 'shrf', 'qr', 'cst', 'scoor', 'nsm', 'naupd')
            self.temp.append(SimpleNamespace(**dict(zip(names, values)),
                name=self.temp[0] if self.title else f'p_beam_{values[0]}',
                source_context=self.source_context))
        elif index == 1:
            section = self.temp[-1]
            raw = fields(line)
            section.shape = raw[0].upper() if raw[0].upper().startswith('SECTION_') else ''
            section.dimensions = [number(v, self.dataframe) for v in (raw[1:] if section.shape else raw)]
            insert(self.dataframe.section_beam, section)
        else:
            raise ValueError('SECTION_BEAM: extra section cards are not mapped')
        self.line_number += 1
