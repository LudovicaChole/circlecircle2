from core.fea.parser import Parser
from core.fea.model.lsdyna.control_bulk_viscosity import ControlBulkViscosity


class ControlBulkViscosityParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        q1_raw = line_raw[0:10].strip()
        q2_raw = line_raw[10:20].strip()
        type_raw = line_raw[20:30].strip()
        btype_raw = line_raw[30:40].strip()

        if len(q1_raw) > 0:
            q1 = self.dataframe.parameter[q1_raw[1:]].value if q1_raw.startswith("&") else float(q1_raw)
        else:
            q1 = 0

        if len(q2_raw) > 0:
            q2 = self.dataframe.parameter[q2_raw[1:]].value if q2_raw.startswith("&") else float(q2_raw)
        else:
            q2 = 0

        if len(type_raw) > 0:
            type_c = self.dataframe.parameter[type_raw[1:]].value if type_raw.startswith("&") else float(type_raw)
        else:
            type_c = 0

        if len(btype_raw) > 0:
            btype = self.dataframe.parameter[btype_raw[1:]].value if btype_raw.startswith("&") else float(btype_raw)
        else:
            btype = 0

        uid = len(self.dataframe.control_bulk_viscosity) + 1

        self.dataframe.control_bulk_viscosity[uid] = ControlBulkViscosity(uid=uid,
                                                                          q1=q1,
                                                                          q2=q2,
                                                                          type_c=type_c,
                                                                          btype=btype)

        return