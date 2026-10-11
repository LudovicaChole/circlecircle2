from core.fea.parser import Parser
from core.fea.model.lsdyna.define_curve import DefineCurve
from .card_fields import value


class FunctParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': lambda line: self.temp.append(line.rstrip())}

    def finish(self):
        if not self.temp:
            return
        if len(self.temp) < 3:
            raise ValueError('FUNCT: incomplete cards; expected header, title and points')
        h = self.temp[0]
        cid = value(h[8:16], integer=True)
        if cid in self.dataframe.define_curve:
            raise ValueError(f'Duplicate FUNCT {cid}')
        curve = DefineCurve(uid=cid, sfa=value(h[24:32], default=1), sfo=value(h[32:40], default=1),
                            offa=value(h[40:48]), offo=value(h[48:56]), name=self.temp[1][5:].strip())
        # Common curves use LS-DYNA offsets before scaling; PAM shifts follow scaling.
        curve.offa /= curve.sfa or 1.0
        curve.offo /= curve.sfo or 1.0
        points = [(value(r[16:32]), value(r[32:48])) for r in self.temp[2:] if r.strip()]
        if not points:
            raise ValueError(f'FUNCT {cid}: no points')
        curve.a1, curve.o1 = map(list, zip(*points))
        self.dataframe.define_curve[cid] = curve
        self.reset()
