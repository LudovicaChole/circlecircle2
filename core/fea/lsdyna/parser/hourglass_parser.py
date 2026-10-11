from core.fea.parser import Parser
from core.fea.model.lsdyna.hourglass import Hourglass
from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.validation import required_id


class HourglassParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = dict.fromkeys(('12.0', '13.0', '16.0'), self._12p0)

    def _12p0(self, line_raw):
        raw = fields(line_raw)
        hgid = required_id(raw[0], 'HGID', self.dataframe)
        values = {name: number(raw[i], self.dataframe, default=default, integer=integer)
                  for i, (name, default, integer) in enumerate([
                      ('ihq', 0, True), ('qm', .1, False), ('ibq', 0, True),
                      ('q1', 1.5, False), ('q2', .06, False)], 1)}
        # Keep unspecified QB/VDC unresolved: its default depends on IHQ.
        values['qb'] = number(raw[6], self.dataframe) if raw[6] else None
        values['qw'] = number(raw[7], self.dataframe, default=values['qm'])
        self.dataframe.hourglass[hgid] = Hourglass(uid=hgid, **values)
        return self.dataframe.hourglass[hgid]
