from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.section_solid import SectionSolid


class SectionSolidTitleParser(Parser):
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
            secid_raw = fields(line_raw)[0]
            elform_raw = fields(line_raw)[1]

            name = name_raw
            secid = number(secid_raw, self.dataframe, integer=True)
            elform = number(elform_raw, self.dataframe, integer=True)

            self.dataframe.section_solid[secid] = SectionSolid(uid=secid,
                                                               elform=elform,
                                                               name=name)

            self.reset()

            return

