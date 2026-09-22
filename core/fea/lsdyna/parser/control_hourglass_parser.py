from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class ControlHourglassParser(Parser):
    """LS-DYNA R12 keyword manual: *CONTROL_HOURGLASS."""
    def __init__(self):
        super().__init__()
        self.version = {"12.0": self._read, "13.0": self._read}

    def _read(self, line_raw):
        spec = [('ihq', 1), ('qh', 0.1)]
        values = fields(line_raw)
        data = {name: number(values[i], self.dataframe, default) for i, (name, default) in enumerate(spec)}
        store = self.dataframe.storge.setdefault('control_hourglass', {})
        uid = len(store) + 1
        store[uid] = SimpleNamespace(uid=uid, **data)
