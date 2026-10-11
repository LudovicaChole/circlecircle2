from core.fea.parser import Parser
from core.fea.model.lsdyna.part import Part
from core.fea.model.lsdyna.section_shell import SectionShell
from core.fea.model.lsdyna.section_solid import SectionSolid
from core.fea.mesh_data import insert
from .card_fields import identifier, value


class PartParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        if line_raw.lstrip().startswith('$'):
            if 'OFFSET' in line_raw:
                self.offset_column = 15 if 'NINT' in line_raw else 10
            return
        if not self.temp:
            self.temp = [line_raw]
        elif line_raw.startswith('NAME'):
            self.name = line_raw[4:].strip()
        elif line_raw.startswith(('RMAT', 'META')):
            raise ValueError('PART: RMAT/META reference requires explicit conversion')
        else:
            self.temp.append(line_raw.rstrip('\r\n'))

    def reset(self):
        super().reset()
        self.name = ''
        self.offset_column = None

    def finish(self):
        if not self.temp:
            return
        header, *cards = self.temp
        pid, mid = identifier(header[8:16]), identifier(header[24:32])
        kind = header[16:24].strip().upper()
        if kind not in ('SHELL', 'SOLID'):
            raise ValueError(f'PART {pid}: unsupported ATYPE {kind}')
        if len(cards) < 3:
            raise ValueError(f'PART {pid}: incomplete property cards')
        part = Part(uid=pid, secid=pid, mid=mid, name=self.name or f'part_{pid}')
        insert(self.dataframe.part, part)
        if kind == 'SHELL':
            h = value(cards[2][:10])
            column = self.offset_column
            if column is None:
                column = 15 if cards[2][10:15].strip() else 10
            offset = value(cards[2][column:column+10])
            nip = value(cards[2][10:15], integer=True, default=5) if column == 15 else 5
            if offset:
                raise ValueError(f'PART {pid}: nonzero shell OFFSET needs reference-surface conversion')
            section = SectionShell(uid=pid, t1=h, t2=h, t3=h, t4=h, name=f'p_shell_{pid}', nip=nip)
            insert(self.dataframe.section_shell, section)
        else:
            insert(self.dataframe.section_solid, SectionSolid(uid=pid, elform=1, name=f'p_solid_{pid}'))
        self.reset()
