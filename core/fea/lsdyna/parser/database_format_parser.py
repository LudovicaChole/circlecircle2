from core.fea.parser import Parser
from core.fea.model.lsdyna.database_format import DatabaseFormat


class DatabaseFormatParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        iform_raw = line_raw[0:10]
        ibinary_raw = line_raw[10:20]

        if len(iform_raw) > 0:
            iform = self.dataframe.parameter[iform_raw[1:]].value if iform_raw.startswith("&") else int(iform_raw)
        else:
            iform = 0

        if len(ibinary_raw) > 0:
            ibinary = self.dataframe.parameter[ibinary_raw[1:]].value if ibinary_raw.startswith("&") else int(ibinary_raw)
        else:
            ibinary = 0

        uid = len(self.dataframe.database_deforc) + 1

        self.dataframe.database_format[uid] = DatabaseFormat(uid=uid,
                                                             iform=iform,
                                                             ibinary=ibinary)

        return