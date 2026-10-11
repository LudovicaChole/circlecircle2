from core.fea.parser import Parser
from core.fea.model.lsdyna.control_timestep import ControlTimestep
from core.fea.lsdyna.parser.card_fields import fields, number


class ControlTimestepParser(Parser):
    """R13 Vol. I 12-549: required card 1 and optional mass-scaling card 2."""
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self._12p0)

    def _12p0(self, line_raw):
        if self.line_number >= 2:
            raise ValueError('CONTROL_TIMESTEP: expected at most two data cards')
        raw = fields(line_raw)
        if self.line_number == 0:
            schema = [('dtinit', 0, False), ('tssfac', 1, False),
                      ('isdo', 2, True), ('tslimt', 3, False),
                      ('dt2ms', 4, False), ('lctm', 5, True),
                      ('erode', 6, True), ('ms1st', 7, True)]
        else:
            schema = [('dt2msf', 0, False), ('dt2mslc', 1, True),
                      ('imscl', 2, True), ('rmscl', 5, False), ('ihdo', 7, True)]
        values = {}
        for name, column, integer in schema:
            try:
                values[name] = number(raw[column], self.dataframe, integer=integer)
            except (ValueError, KeyError) as error:
                raise ValueError(f'CONTROL_TIMESTEP card {self.line_number+1} '
                                 f'{name.upper()}={raw[column]!r}: {error}') from error
        if self.line_number == 0:
            uid = max(self.dataframe.control_timestep, default=0)+1
            record = ControlTimestep(uid=uid, **values)
            self.dataframe.control_timestep[uid] = record
            self.temp = [record]
        else:
            record = self.temp[0]
            for name, value in values.items():
                setattr(record, name, value)
            record.has_optional_card = True
        self.line_number += 1
