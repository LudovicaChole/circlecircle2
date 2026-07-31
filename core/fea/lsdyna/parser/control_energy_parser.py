from core.fea.parser import Parser
from core.fea.lsdyna.keywords.control_energy import ControlEnergy


class ControlEnergyParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

    def _12p0(self, line_raw):
        hgen_raw = line_raw[0:10].strip()
        rwen_raw = line_raw[10:20].strip()
        slnten_raw = line_raw[20:30].strip()
        rylen_raw = line_raw[30:40].strip()
        irgen_raw = line_raw[40:50].strip()

        if len(hgen_raw) > 0:
            hgen = self.dataframe.parameter[hgen_raw[1:]] if hgen_raw.startswith("&") else int(hgen_raw)
        else:
            hgen = 0

        if len(rwen_raw) > 0:
            rwen = self.dataframe.parameter[rwen_raw[1:]] if rwen_raw.startswith("&") else int(rwen_raw)
        else:
            rwen = 0

        if len(slnten_raw) > 0:
            slnten = self.dataframe.parameter[slnten_raw[1:]] if slnten_raw.startswith("&") else int(slnten_raw)
        else:
            slnten = 0

        if len(rylen_raw) > 0:
            rylen = self.dataframe.parameter[rylen_raw[1:]] if rylen_raw.startswith("&") else float(rylen_raw)
        else:
            rylen = 0

        uid = len(self.dataframe.control_energy) + 1

        self.dataframe.control_energy[uid] = ControlEnergy(uid=uid,
                                                           hgen=hgen,
                                                           rwen=rwen,
                                                           slnten=slnten,
                                                           rylen=rylen,)

        return
