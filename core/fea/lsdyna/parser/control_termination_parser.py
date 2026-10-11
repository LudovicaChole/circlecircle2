from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.control_termination import ControlTermination


class ControlTerminationParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        endtim_raw = fields(line_raw)[0]
        endcyc_raw = fields(line_raw)[1]
        dtmin_raw = fields(line_raw)[2]
        endeng_raw = fields(line_raw)[3]
        endmas_raw = fields(line_raw)[4]
        nosol_raw = fields(line_raw)[5]

        if len(endtim_raw) > 0:
            endtim = number(endtim_raw, self.dataframe)
        else:
            endtim = 0

        if len(endcyc_raw) > 0:
            endcyc = number(endcyc_raw, self.dataframe)
        else:
            endcyc = 0

        if len(dtmin_raw) > 0:
            dtmin = number(dtmin_raw, self.dataframe)
        else:
            dtmin = 0

        if len(endeng_raw) > 0:
            endeng = number(endeng_raw, self.dataframe)
        else:
            endeng = 0

        if len(endmas_raw) > 0:
            endmas = number(endmas_raw, self.dataframe)
        else:
            endmas = 0

        if len(nosol_raw) > 0:
            nosol = number(nosol_raw, self.dataframe)
        else:
            nosol = 0

        uid = len(self.dataframe.control_termination) + 1

        self.dataframe.control_termination[uid] = ControlTermination(uid=uid,
                                                                     endtim=endtim,
                                                                     endcyc=endcyc,
                                                                     dtmin=dtmin,
                                                                     endeng=endeng,
                                                                     endmas=endmas,
                                                                     nosol=nosol,)

        return
