from core.fea.parser import Parser
from core.fea.model.lsdyna.database_binary_intfor import DatabaseBinaryIntfor


class DatabaseBinaryIntforParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        dt_raw = line_raw[0:10].strip()
        lcdt_raw = line_raw[10:20].strip()

        if len(dt_raw) > 0:
            dt = self.dataframe.parameter[dt_raw[1:]].value if dt_raw.startswith("&") else float(dt_raw)
        else:
            dt = 0

        if len(lcdt_raw) > 0:
            lcdt = self.dataframe.parameter[lcdt_raw[1:]].value if lcdt_raw.startswith("&") else int(lcdt_raw)
        else:
            lcdt = 0

        uid = len(self.dataframe.database_binary_intfor) + 1

        self.dataframe.database_binary_intfor[uid] = DatabaseBinaryIntfor(uid=uid,
                                                                          dt=dt,
                                                                          lcdt=lcdt)

        return