from core.fea.parser import Parser
from core.fea.lsdyna.keywords.database_nodout import DatabaseNodout


class DatabaseNodoutParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

    def _12p0(self, line_raw):
        dt_raw = line_raw[0:10].strip()
        binary_raw = line_raw[10:20].strip()
        lcur_raw = line_raw[20:30].strip()
        ioopt_raw = line_raw[30:40].strip()
        dthf_raw = line_raw[40:50].strip()
        binhf_raw = line_raw[50:60].strip()

        if len(dt_raw) > 0:
            dt = self.dataframe.parameter[dt_raw[1:]].value if dt_raw.startswith("&") else float(dt_raw)
        else:
            dt = 0

        if len(binary_raw) > 0:
            binary = self.dataframe.parameter[binary_raw[1:]].value if binary_raw.startswith("&") else int(binary_raw)
        else:
            binary = 0

        if len(lcur_raw) > 0:
            lcur = self.dataframe.parameter[lcur_raw[1:]].value if lcur_raw.startswith("&") else float(lcur_raw)
        else:
            lcur = 0

        if len(ioopt_raw) > 0:
            ioopt = self.dataframe.parameter[ioopt_raw[1:]].value if ioopt_raw.startswith("&") else float(ioopt_raw)
        else:
            ioopt = 0

        if len(dthf_raw) > 0:
            dthf = self.dataframe.parameter[dthf_raw[1:]].value if dthf_raw.startswith("&") else float(dthf_raw)
        else:
            dthf = 0

        if len(binhf_raw) > 0:
            binhf = self.dataframe.parameter[binhf_raw[1:]].value if binhf_raw.startswith("&") else float(binhf_raw)
        else:
            binhf = 0

        uid = len(self.dataframe.database_nodout) + 1

        self.dataframe.database_nodout[uid] = DatabaseNodout(uid=uid,
                                                             dt=dt,
                                                             binary=binary,
                                                             lcur=lcur,
                                                             ioopt=ioopt,
                                                             dthf=dthf,
                                                             binhf=binhf)

        return