from core.fea.parser import Parser
from core.fea.model.lsdyna.define_table import DefineTable


class DefineTableTitleParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

        self.current_table_id = None

    def _12p0(self, line_raw):
        if self.line_number == 0:
            name_raw = line_raw.strip()

            self.temp.append(name_raw)
            self.line_number = 1

            return

        if self.line_number == 1:
            name_raw = self.temp[0]
            tbid_raw = line_raw[0:10].strip()
            sfa_raw = line_raw[10:20].strip()
            offa_raw = line_raw[20:30].strip()

            name = name_raw
            tbid = self.dataframe.parameter[tbid_raw[1:]].value if tbid_raw.startswith("&") else int(tbid_raw)

            if len(sfa_raw) > 0:
                sfa = self.dataframe.parameter[sfa_raw[1:]].value if sfa_raw.startswith("&") else float(sfa_raw)
            else:
                sfa = 1.0

            if len(offa_raw) > 0:
                offa = self.dataframe.parameter[offa_raw[1:]].value if offa_raw.startswith("&") else float(offa_raw)
            else:
                offa = 0.0

            self.dataframe.define_table[tbid] = DefineTable(uid=tbid, sfa=sfa, offa=offa, name=name)
            self.current_table_id = tbid

            self.line_number = 2

            return

        if self.line_number != 0 and self.line_number != 1:
            value_raw = line_raw[0:20]
            lcid_raw = line_raw[20:40]

            value = value_raw[1:] if value_raw.startswith("&") else float(value_raw)
            lcid = lcid_raw[1:] if lcid_raw.startswith("&") else int(lcid_raw)

            self.dataframe.define_table[self.current_table_id].value.append(value)
            self.dataframe.define_table[self.current_table_id].lcid.append(lcid)

            return
