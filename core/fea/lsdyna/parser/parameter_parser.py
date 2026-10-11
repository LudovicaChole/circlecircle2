"""R13 Vol. I 34-2: four PRMR/VAL pairs, each field ten columns."""
import re
from core.fea.parser import Parser
from core.fea.model.lsdyna.parameter import Parameter
from core.fea.lsdyna.parser.card_fields import fields, number


class ParameterParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self._12p0)

    def _12p0(self, line_raw):
        text = line_raw.split('$', 1)[0].rstrip('\r\n')
        if not text.strip():
            return
        if (',' in text and len(text.split(',')) > 8) or (',' not in text and text[80:].strip()):
            raise ValueError('PARAMETER: expected at most four PRMR/VAL pairs')
        raw = fields(text)
        pending = []
        for i in range(0, 8, 2):
            declaration, value = raw[i:i+2]
            if not declaration and not value:
                continue
            kind, name = declaration[:1].upper(), declaration[1:].strip()
            if kind not in ('R', 'I', 'C') or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]{0,8}', name):
                raise ValueError(f'PARAMETER: invalid declaration {declaration!r}')
            if name.lower() == 'time':
                raise ValueError('PARAMETER: time is a reserved name')
            if not value:
                raise ValueError(f'PARAMETER {name}: missing value')
            try:
                resolved = value if kind == 'C' else number(value, self.dataframe, integer=kind == 'I')
            except (ValueError, KeyError) as error:
                raise ValueError(f'PARAMETER {name}: {error}') from error
            pending.append((name, Parameter(kind, name, resolved)))
        for name, record in pending:
            self.dataframe.parameter[name] = record
