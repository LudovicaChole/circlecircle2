from types import SimpleNamespace
from core.fea.parser import Parser
from .card_fields import fields, number


class ElementMassParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {"12.0": self._read, "13.0": self._read, "16.0": self._read}

    def _read(self, line_raw):
        if not line_raw.strip():
            return
        values = fields(line_raw, (8, 8, 16, 8))
        eid, nid, mass, pid = [number(v, self.dataframe, integer=i != 2) for i, v in enumerate(values)]
        if eid <= 0 or nid <= 0 or mass < 0:
            raise ValueError(f'Invalid ELEMENT_MASS {eid}')
        self.dataframe.storge.setdefault('element_mass', {})[eid] = SimpleNamespace(uid=eid, nid=nid, mass=mass, pid=pid)
