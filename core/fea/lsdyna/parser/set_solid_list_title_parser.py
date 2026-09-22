from core.fea.parser import Parser
from core.fea.lsdyna.keywords.set_node_list import SetNodeList


class SetSolidListTitleParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

        self.current_set_list_id = None

    def _12p0(self, line_raw):
        if self.line_number == 0:
            name_raw = line_raw.strip()

            self.temp.append(name_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            name_raw = self.temp[0]

            sid_raw = line_raw[0:10].strip()
            da1_raw = line_raw[10:20].strip()
            da2_raw = line_raw[20:30].strip()
            da3_raw = line_raw[30:40].strip()
            da4_raw = line_raw[40:50].strip()
            solver_raw = line_raw[50:60].strip()

            name = name_raw

            sid = self.dataframe.parameter[sid_raw[1:]].value if sid_raw.startswith("&") else int(sid_raw)

            if len(da1_raw) > 0:
                da1 = self.dataframe.parameter[da1_raw[1:]].value if da1_raw.startswith("&") else float(da1_raw)
            else:
                da1 = 0.0

            if len(da2_raw) > 0:
                da2 = self.dataframe.parameter[da2_raw[1:]].value if da2_raw.startswith("&") else float(da2_raw)
            else:
                da2 = 0.0

            if len(da3_raw) > 0:
                da3 = self.dataframe.parameter[da3_raw[1:]].value if da3_raw.startswith("&") else float(da3_raw)
            else:
                da3 = 0.0

            if len(da4_raw) > 0:
                da4 = self.dataframe.parameter[da4_raw[1:]].value if da4_raw.startswith("&") else float(da4_raw)
            else:
                da4 = 0.0

            if len(solver_raw) > 0:
                solver = solver_raw
            else:
                solver = "MECH"

            self.dataframe.storge.setdefault("set_solid_list", {})[sid] = SetNodeList(uid=sid,
                                                            da1=da1,
                                                            da2=da2,
                                                            da3=da3,
                                                            da4=da4,
                                                            solver=solver,
                                                            name=name)

            self.current_set_list_id = sid

            self.line_number = 2

            return

        if self.line_number != 0 and self.line_number != 1:
            data_list = line_raw.split()

            current_set_list_object = self.dataframe.storge.setdefault("set_solid_list", {})[self.current_set_list_id]

            current_set_list_object.ids.extend(data_list)

