"""R13 INITIAL_VELOCITY: node-set velocities, with optional exempt set."""
from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class InitialVelocityParser(Parser):
    cards = 2

    def __init__(self):
        super().__init__()
        self.version = {v: self._read for v in ('12.0', '13.0', '16.0')}

    def _read(self, line_raw):
        raw = fields(line_raw)
        if self.line_number == 0:
            values = [number(v, self.dataframe, integer=True) for v in raw[:5]]
            nsid, nsidex, boxid, irigid, icid = values
            if nsid < 0 or nsidex < 0:
                raise ValueError('INITIAL_VELOCITY: NSID and NSIDEX must be nonnegative')
            if boxid or irigid or icid:
                raise ValueError('INITIAL_VELOCITY: BOXID, IRIGID and local ICID options are not mapped')
            self.temp = [SimpleNamespace(nsid=nsid, nsidex=nsidex,
                                        source_context=self.source_context)]
        elif self.line_number in (1, 2) and self.temp:
            obj = self.temp[0]
            components = tuple(number(v, self.dataframe) for v in raw[:6])
            if self.line_number == 1:
                obj.components = components
            else:
                obj.exempt_components = components
            if not obj.nsidex or self.line_number == 2:
                store = self.dataframe.storge['initial_velocity']
                store[len(store) + 1] = obj
                self.temp = []
        else:
            raise ValueError('Unexpected INITIAL_VELOCITY continuation card')
        self.line_number += 1
