from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.database_nodout import DatabaseNodout


class DatabaseNodoutParser(Parser):
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
        dthf_raw = fields(line_raw)[4]
        binhf_raw = fields(line_raw)[5]

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

        if len(dthf_raw) > 0:
            dthf = number(dthf_raw, self.dataframe, integer=False)
        else:
            dthf = 0

        if len(binhf_raw) > 0:
            binhf = number(binhf_raw, self.dataframe, integer=False)
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