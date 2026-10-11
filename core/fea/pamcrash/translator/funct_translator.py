"""Write curve scales and shifts without losing LS-DYNA physical coordinates."""
from core.fea.translator import Translator
from .selection import field


class FunctTranslator(Translator):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._write, '2023': self._write}

    def translate(self, version):
        self._write()

    def _write(self):
        lines = self.dataframe.output_storge.setdefault('FUNCT', [])
        for cid, curve in self.dataframe.define_curve.items():
            sx, sy = curve.sfa or 1.0, curve.sfo or 1.0
            lines += ['FUNCT / '+''.join(field(v) for v in (cid,0,sx,sy,curve.offa*sx,curve.offo*sy))+'\n',
                      f'NAME {curve.name}\n']
            lines += [' '*16+field(x,16)+field(y,16)+'\n' for x,y in zip(curve.a1,curve.o1)]
