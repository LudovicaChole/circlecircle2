from core.fea.parser import Parser
from core.fea.model.lsdyna.control_accuracy import ControlAccuracy


class ControlAccuracyParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        osu_raw = line_raw[0:10].strip()
        inn_raw = line_raw[10:20].strip()
        pidosu_raw = line_raw[20:30].strip()
        iacc_raw = line_raw[30:40].strip()

        if len(osu_raw) > 0:
            osu = self.dataframe.parameter[osu_raw[1:]].value if osu_raw.startswith("&") else int(osu_raw)
        else:
            osu = 0

        if len(inn_raw) > 0:
            inn = self.dataframe.parameter[inn_raw[1:]].value if inn_raw.startswith("&") else int(inn_raw)
        else:
            inn = 0

        if len(pidosu_raw) > 0:
            pidosu = self.dataframe.parameter[pidosu_raw[1:]].value if pidosu_raw.startswith("&") else float(pidosu_raw)
        else:
            pidosu = 0

        if len(iacc_raw) > 0:
            iacc = self.dataframe.parameter[iacc_raw[1:]].value if iacc_raw.startswith("&") else float(iacc_raw)
        else:
            iacc = 0

        uid = len(self.dataframe.control_accuracy) + 1

        self.dataframe.control_accuracy[uid] = ControlAccuracy(uid=uid,
                                                               osu=osu,
                                                               inn=inn,
                                                               pidosu=pidosu,
                                                               iacc=iacc)

        return
