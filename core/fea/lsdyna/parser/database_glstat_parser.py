from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.database_glstat import DatabaseGlstat


class DatabaseGlstatParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        dt_raw = fields(line_raw)[0]
        binary_raw = fields(line_raw)[1]
        lcur_raw = fields(line_raw)[2]
        ioopt_raw = fields(line_raw)[3]

        if len(dt_raw) > 0:
            dt = number(dt_raw, self.dataframe, integer=False)
        else:
            dt = 0

        if len(binary_raw) > 0:
            binary = number(binary_raw, self.dataframe, integer=True)
        else:
            binary = 0

        if len(lcur_raw) > 0:
            lcur = number(lcur_raw, self.dataframe, integer=False)
        else:
            lcur = 0

        if len(ioopt_raw) > 0:
            ioopt = number(ioopt_raw, self.dataframe, integer=False)
        else:
            ioopt = 0

        uid = len(self.dataframe.database_glstat) + 1

        self.dataframe.database_glstat[uid] = DatabaseGlstat(uid=uid,
                                                             dt=dt,
                                                             binary=binary,
                                                             lcur=lcur,
                                                             ioopt=ioopt)

        return
