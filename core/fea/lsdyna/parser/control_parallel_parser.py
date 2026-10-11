from core.fea.parser import Parser
from core.fea.model.lsdyna.control_parallel import ControlParallel


class ControlParallelParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        ncpu_raw = line_raw[0:10].strip()
        numrhs_raw = line_raw[10:20].strip()
        const_raw = line_raw[20:30].strip()
        para_raw = line_raw[30:40].strip()

        if len(ncpu_raw) > 0:
            ncpu = self.dataframe.parameter[ncpu_raw[1:]].value if ncpu_raw.startswith("&") else int(ncpu_raw)
        else:
            ncpu = 0

        if len(numrhs_raw) > 0:
            numrhs = self.dataframe.parameter[numrhs_raw[1:]].value if numrhs_raw.startswith("&") else int(numrhs_raw)
        else:
            numrhs = 0

        if len(const_raw) > 0:
            const = self.dataframe.parameter[const_raw[1:]].value if const_raw.startswith("&") else int(const_raw)
        else:
            const = 0

        if len(para_raw) > 0:
            para = self.dataframe.parameter[para_raw[1:]].value if para_raw.startswith("&") else int(para_raw)
        else:
            para = 0

        uid = len(self.dataframe.control_parallel) + 1

        self.dataframe.control_parallel[uid] = ControlParallel(uid=uid,
                                                               ncpu=ncpu,
                                                               numrhs=numrhs,
                                                               const=const,
                                                               para=para)

        return