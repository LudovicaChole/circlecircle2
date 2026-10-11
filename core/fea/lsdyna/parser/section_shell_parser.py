from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.section_shell import SectionShell


class SectionShellParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            secid_raw = fields(line_raw)[0]
            elform_raw = fields(line_raw)[1]
            shrf_raw = fields(line_raw)[2]
            nip_raw = fields(line_raw)[3]

            self.temp.append(secid_raw)
            self.temp.append(elform_raw)
            self.temp.append(shrf_raw)
            self.temp.append(nip_raw)
            self.line_number = 1

            return

        if self.line_number == 1:
            secid_raw = self.temp[0]
            elform_raw = self.temp[1]
            shrf_raw = self.temp[2]
            nip_raw = self.temp[3]

            t1_raw = fields(line_raw)[0]
            t2_raw = fields(line_raw)[1]
            t3_raw = fields(line_raw)[2]
            t4_raw = fields(line_raw)[3]

            if len(secid_raw) > 0:
                secid = number(secid_raw, self.dataframe, integer=True)
            else:
                secid = 0

            if len(elform_raw) > 0:
                elform = number(elform_raw, self.dataframe, integer=True)
            else:
                elform = 0

            if len(shrf_raw) > 0:
                shrf = number(shrf_raw, self.dataframe, integer=False)
            else:
                shrf = 1.0

            if len(nip_raw) > 0:
                nip = number(nip_raw, self.dataframe, integer=False)
            else:
                nip = 2

            t1 = number(t1_raw, self.dataframe, default=0)
            t2 = number(t2_raw, self.dataframe, default=t1)
            t3 = number(t3_raw, self.dataframe, default=t1)
            t4 = number(t4_raw, self.dataframe, default=t1)

            self.dataframe.section_shell[secid] = SectionShell(
                uid=secid,
                elform=elform,
                shrf=shrf,
                nip=nip,
                t1=t1,
                t2=t2,
                t3=t3,
                t4=t4,
            )

            self.reset()

            return

