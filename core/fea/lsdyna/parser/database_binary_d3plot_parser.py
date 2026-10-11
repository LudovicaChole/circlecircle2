from core.fea.parser import Parser
from core.fea.model.lsdyna.database_binary_d3plot import DatabaseBinaryD3plot
from core.fea.lsdyna.parser.card_fields import fields, number


class DatabaseBinaryD3plotParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self._12p0)

    def _12p0(self, line_raw):
        if self.line_number >= 2:
            raise ValueError('DATABASE_BINARY_D3PLOT: expected at most two cards')
        names = (('dt', 'lcdt', 'beam', 'npltc', 'psepid') if self.line_number == 0
                 else ('ioopt', 'rate', 'cutoff', 'window', 'ptype', 'pset'))
        raw = fields(line_raw)
        values = {}
        for name, value in zip(names, raw):
            try:
                values[name] = number(value, self.dataframe, integer=name in ('lcdt', 'beam', 'npltc', 'psepid', 'ioopt', 'ptype', 'pset'))
            except (ValueError, KeyError) as error:
                raise ValueError(f'DATABASE_BINARY_D3PLOT {name.upper()}: {error}') from error
        if self.line_number == 0:
            store = self.dataframe.database_binary_d3plot
            record = DatabaseBinaryD3plot(uid=max(store, default=0)+1, **values)
            store[record.uid] = record
            self.temp = [record]
        else:
            for name, value in values.items():
                setattr(self.temp[0], name, value)
        self.line_number += 1
