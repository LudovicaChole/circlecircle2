from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.part import Part


class PartParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            name_raw = line_raw.strip()
            self.temp.append(name_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            name_raw = self.temp[0]
            pid_raw = fields(line_raw)[0]
            secid_raw = fields(line_raw)[1]
            mid_raw = fields(line_raw)[2]
            eosid_raw = fields(line_raw)[3]
            hgid_raw = fields(line_raw)[4]

            name = name_raw

            if len(pid_raw) > 0:
                pid = number(pid_raw, self.dataframe, integer=True)
            else:
                pid = 0

            if len(secid_raw) > 0:
                secid = number(secid_raw, self.dataframe, integer=True)
            else:
                secid = 0

            if len(mid_raw) > 0:
                mid = number(mid_raw, self.dataframe, integer=True)
            else:
                mid = 0

            if len(eosid_raw) > 0:
                eosid = number(eosid_raw, self.dataframe, integer=True)
            else:
                eosid = 0

            if len(hgid_raw) > 0:
                hgid = number(hgid_raw, self.dataframe, integer=True)
            else:
                hgid = 0

            self.dataframe.part[pid] = Part(name, pid, secid, mid, eosid, hgid,
                tmid=number(fields(line_raw)[7], self.dataframe, integer=True))
            self.dataframe.part_tensor.append([pid, secid, mid, eosid, hgid])

            self.reset()

            return

