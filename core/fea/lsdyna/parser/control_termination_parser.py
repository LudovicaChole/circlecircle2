from core.fea.parser import Parser
from core.fea.lsdyna.keywords.control_termination import ControlTermination


class ControlTerminationParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

    def _12p0(self, line_raw):
        endtim_raw = line_raw[0:10].strip()
        endcyc_raw = line_raw[10:20].strip()
        dtmin_raw = line_raw[20:30].strip()
        endeng_raw = line_raw[30:40].strip()
        endmas_raw = line_raw[40:50].strip()
        nosol_raw = line_raw[50:60].strip()

        if len(endtim_raw) > 0:
            endtim = self.dataframe.parameter[endtim_raw[1:]] if endtim_raw.startswith("&") else float(endtim_raw)
        else:
            endtim = 0

        if len(endcyc_raw) > 0:
            endcyc = self.dataframe.parameter[endcyc_raw[1:]] if endcyc_raw.startswith("&") else float(endcyc_raw)
        else:
            endcyc = 0

        if len(dtmin_raw) > 0:
            dtmin = self.dataframe.parameter[dtmin_raw[1:]] if dtmin_raw.startswith("&") else float(dtmin_raw)
        else:
            dtmin = 0

        if len(endeng_raw) > 0:
            endeng = self.dataframe.parameter[endeng_raw[1:]] if endeng_raw.startswith("&") else float(endeng_raw)
        else:
            endeng = 0

        if len(endmas_raw) > 0:
            endmas = self.dataframe.parameter[endmas_raw[1:]] if endmas_raw.startswith("&") else float(endmas_raw)
        else:
            endmas = 0

        if len(nosol_raw) > 0:
            nosol = self.dataframe.parameter[nosol_raw[1:]] if nosol_raw.startswith("&") else float(nosol_raw)
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
