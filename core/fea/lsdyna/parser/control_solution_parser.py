from core.fea.parser import Parser
from core.fea.model.lsdyna.control_solution import ControlSolution


class ControlSolutionParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        soln_raw = line_raw[0:10].strip()
        nlq_raw = line_raw[10:20].strip()
        isnan_raw = line_raw[20:30].strip()
        lcint_raw = line_raw[30:40].strip()
        lcacc_raw = line_raw[40:50].strip()
        ncdcf_raw = line_raw[50:60].strip()

        if len(soln_raw) > 0:
            soln = self.dataframe.parameter[soln_raw[1:]].value if soln_raw.startswith("&") else float(soln_raw)
        else:
            soln = 0

        if len(nlq_raw) > 0:
            nlq = self.dataframe.parameter[nlq_raw[1:]].value if nlq_raw.startswith("&") else float(nlq_raw)
        else:
            nlq = 0

        if len(isnan_raw) > 0:
            isnan = self.dataframe.parameter[isnan_raw[1:]].value if isnan_raw.startswith("&") else int(isnan_raw)
        else:
            isnan = 0

        if len(lcint_raw) > 0:
            lcint = self.dataframe.parameter[lcint_raw[1:]].value if lcint_raw.startswith("&") else float(lcint_raw)
        else:
            lcint = 0

        if len(lcacc_raw) > 0:
            lcacc = self.dataframe.parameter[lcacc_raw[1:]].value if lcacc_raw.startswith("&") else float(lcacc_raw)
        else:
            lcacc = 0

        if len(ncdcf_raw) > 0:
            ncdcf = self.dataframe.parameter[ncdcf_raw[1:]].value if ncdcf_raw.startswith("&") else float(ncdcf_raw)
        else:
            ncdcf = 0

        uid = len(self.dataframe.control_solution) + 1

        self.dataframe.control_solution[uid] = ControlSolution(uid=uid,
                                                               soln=soln,
                                                               nlq=nlq,
                                                               isnan=isnan,
                                                               lcint=lcint,
                                                               lcacc=lcacc,
                                                               ncdcf=ncdcf)

        return