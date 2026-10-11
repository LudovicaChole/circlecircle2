from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.mat_rigid import MatRigid


class MatRigidParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            mid_raw = fields(line_raw)[0]
            rho_raw = fields(line_raw)[1]
            e_raw = fields(line_raw)[2]
            pr_raw = fields(line_raw)[3]
            n_raw = fields(line_raw)[4]
            couple_raw = fields(line_raw)[5]
            m_raw = fields(line_raw)[6]
            alias_raw = fields(line_raw)[7]

            self.temp.append(mid_raw)
            self.temp.append(rho_raw)
            self.temp.append(e_raw)
            self.temp.append(pr_raw)
            self.temp.append(n_raw)
            self.temp.append(couple_raw)
            self.temp.append(m_raw)
            self.temp.append(alias_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            cmo_raw = fields(line_raw)[0]
            con1_raw = fields(line_raw)[1]
            con2_raw = fields(line_raw)[2]

            self.temp.append(cmo_raw)
            self.temp.append(con1_raw)
            self.temp.append(con2_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            mid_raw = self.temp[0]
            rho_raw = self.temp[1]
            e_raw = self.temp[2]
            pr_raw = self.temp[3]
            n_raw = self.temp[4]
            couple_raw = self.temp[5]
            m_raw = self.temp[6]
            alias_raw = self.temp[7]
            cmo_raw = self.temp[8]
            con1_raw = self.temp[9]
            con2_raw = self.temp[10]
            a1_raw = fields(line_raw)[0]
            a2_raw = fields(line_raw)[1]
            a3_raw = fields(line_raw)[2]
            v1_raw = fields(line_raw)[3]
            v2_raw = fields(line_raw)[4]
            v3_raw = fields(line_raw)[5]

            mid = number(mid_raw, self.dataframe, integer=True)
            rho = number(rho_raw, self.dataframe, integer=False)
            e = number(e_raw, self.dataframe, integer=False)
            pr = number(pr_raw, self.dataframe, integer=False)

            if len(n_raw) > 0:
                n = number(n_raw, self.dataframe, integer=False)
            else:
                n = 0.0

            if len(couple_raw) > 0:
                couple = number(couple_raw, self.dataframe, integer=False)
            else:
                couple = 0.0

            if len(m_raw) > 0:
                m = number(m_raw, self.dataframe, integer=False)
            else:
                m = 0.0

            if len(alias_raw) > 0:
                alias = number(alias_raw, self.dataframe, integer=False)
            else:
                alias = 0.0

            if len(cmo_raw) > 0:
                cmo = number(cmo_raw, self.dataframe, integer=False)
            else:
                cmo = 0.0

            if len(con1_raw) > 0:
                con1 = number(con1_raw, self.dataframe, integer=True)
            else:
                con1 = 0

            if len(con2_raw) > 0:
                con2 = number(con2_raw, self.dataframe, integer=True)
            else:
                con2 = 0

            if len(a1_raw) > 0:
                a1 = number(a1_raw, self.dataframe, integer=False)
            else:
                a1 = 0.0

            if len(a2_raw) > 0:
                a2 = number(a2_raw, self.dataframe, integer=False)
            else:
                a2 = 0.0

            if len(a3_raw) > 0:
                a3 = number(a3_raw, self.dataframe, integer=False)
            else:
                a3 = 0.0

            if len(v1_raw) > 0:
                v1 = number(v1_raw, self.dataframe, integer=False)
            else:
                v1 = 0.0

            if len(v2_raw) > 0:
                v2 = number(v2_raw, self.dataframe, integer=False)
            else:
                v2 = 0.0

            if len(v3_raw) > 0:
                v3 = number(v3_raw, self.dataframe, integer=False)
            else:
                v3 = 0.0

            self.dataframe.material[mid] = MatRigid(uid=mid,
                                                    rho=rho,
                                                    e=e,
                                                    pr=pr,
                                                    n=n,
                                                    couple=couple,
                                                    m=m,
                                                    alias=alias,
                                                    cmo=cmo,
                                                    con1=con1,
                                                    con2=con2,
                                                    a1=a1,
                                                    a2=a2,
                                                    a3=a3,
                                                    v1=v1,
                                                    v2=v2,
                                                    v3=v3)

            self.dataframe.storge_material_id.append(mid)

            self.reset()

            return

