from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.mat_elastic import MatElastic


class MatElasticParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        mid_raw = fields(line_raw)[0]
        rho_raw = fields(line_raw)[1]
        e_raw = fields(line_raw)[2]
        pr_raw = fields(line_raw)[3]
        da_raw = fields(line_raw)[4]
        db_raw = fields(line_raw)[5]
        k_raw = fields(line_raw)[6]

        mid = number(mid_raw, self.dataframe, integer=True)
        rho = number(rho_raw, self.dataframe, integer=False)
        e = number(e_raw, self.dataframe, integer=False)
        pr = number(pr_raw, self.dataframe, integer=False)

        if len(da_raw) > 0:
            da = number(da_raw, self.dataframe, integer=False)
        else:
            da = 0

        if len(db_raw) > 0:
            db = number(db_raw, self.dataframe, integer=False)
        else:
            db = 0

        if len(k_raw) > 0:
            k = number(k_raw, self.dataframe, integer=False)
        else:
            k = 0

        self.dataframe.material[mid] = MatElastic(uid=mid,
                                                  rho=rho,
                                                  e=e,
                                                  pr=pr,
                                                  da=da,
                                                  db=db,
                                                  k=k)

        self.dataframe.storge_material_id.append(mid)

        self.reset()

        return

