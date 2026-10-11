from core.fea.parser import Parser
from core.fea.model.lsdyna.control_termination import ControlTermination
from .card_fields import value


class RunendParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        text = line_raw.strip()
        if text.startswith('RUNEND'):
            return
        key, raw = text.split(maxsplit=1)
        if key != 'TIME':
            raise ValueError(f'RUNEND: unsupported termination criterion {key}')
        end = value(raw)
        if end <= 0:
            raise ValueError('RUNEND TIME must be positive')
        self.dataframe.control_termination[1] = ControlTermination(uid=1,endtim=end)
