from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.section_solid import SectionSolid


class SectionSolidParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        secid_raw = fields(line_raw)[0]
        elform_raw = fields(line_raw)[1]

        secid = number(secid_raw, self.dataframe, integer=True)
        elform = number(elform_raw, self.dataframe, integer=True)

        self.dataframe.section_solid[secid] = SectionSolid(uid=secid,
                                                           elform=elform)

        self.reset()

        return

