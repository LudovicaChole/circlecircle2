from core.fea.parser import Parser
from core.fea.model.lsdyna.control_dynamic_relaxation import ControlDynamicRelaxation


class ControlDynamicRelaxationParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        nrcyck_raw = line_raw[0:10].strip()
        drtol_raw = line_raw[10:20].strip()
        drfctr_raw = line_raw[20:30].strip()
        drterm_raw = line_raw[30:40].strip()
        tssfdr_raw = line_raw[40:50].strip()
        irelal_raw = line_raw[50:60].strip()
        edttl_raw = line_raw[60:70].strip()
        idrflg_raw = line_raw[70:80].strip()


        if len(nrcyck_raw) > 0:
            nrcyck = self.dataframe.parameter[nrcyck_raw[1:]].value if nrcyck_raw.startswith("&") else float(nrcyck_raw)
        else:
            nrcyck = 0

        if len(drtol_raw) > 0:
            drtol = self.dataframe.parameter[drtol_raw[1:]].value if drtol_raw.startswith("&") else float(drtol_raw)
        else:
            drtol = 0

        if len(drfctr_raw) > 0:
            drfctr = self.dataframe.parameter[drfctr_raw[1:]].value if drfctr_raw.startswith("&") else float(drfctr_raw)
        else:
            drfctr = 0

        if len(drterm_raw) > 0:
            drterm = self.dataframe.parameter[drterm_raw[1:]].value if drterm_raw.startswith("&") else float(drterm_raw)
        else:
            drterm = 0

        if len(tssfdr_raw) > 0:
            tssfdr = self.dataframe.parameter[tssfdr_raw[1:]].value if tssfdr_raw.startswith("&") else float(tssfdr_raw)
        else:
            tssfdr = 0

        if len(irelal_raw) > 0:
            irelal = self.dataframe.parameter[irelal_raw[1:]].value if irelal_raw.startswith("&") else float(irelal_raw)
        else:
            irelal = 0

        if len(edttl_raw) > 0:
            edttl = self.dataframe.parameter[edttl_raw[1:]].value if edttl_raw.startswith("&") else float(edttl_raw)
        else:
            edttl = 0

        if len(idrflg_raw) > 0:
            idrflg = self.dataframe.parameter[idrflg_raw[1:]].value if idrflg_raw.startswith("&") else float(idrflg_raw)
        else:
            idrflg = 0

        uid = len(self.dataframe.control_dynamic_relaxation) + 1

        self.dataframe.control_dynamic_relaxation[uid] = ControlDynamicRelaxation(uid=uid,
                                                                                  nrcyck=nrcyck,
                                                                                  drtol=drtol,
                                                                                  drfctr=drfctr,
                                                                                  drterm=drterm,
                                                                                  tssfdr=tssfdr,
                                                                                  irelal=irelal,
                                                                                  edttl=edttl,
                                                                                  idrflg=idrflg)

        return