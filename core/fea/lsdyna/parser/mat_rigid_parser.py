from core.fea.parser import Parser
from core.fea.lsdyna.keywords.mat_rigid import MatRigid


class MatRigidParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            mid_raw = line_raw[0:10].strip()
            rho_raw = line_raw[10:20].strip()
            e_raw = line_raw[20:30].strip()
            pr_raw = line_raw[30:40].strip()
            n_raw = line_raw[40:50].strip()
            couple_raw = line_raw[50:60].strip()
            m_raw = line_raw[60:70].strip()
            alias_raw = line_raw[70:80].strip()

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
            cmo_raw = line_raw[0:10].strip()
            con1_raw = line_raw[10:20].strip()
            con2_raw = line_raw[20:30].strip()

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
            a1_raw = line_raw[0:10].strip()
            a2_raw = line_raw[10:20].strip()
            a3_raw = line_raw[20:30].strip()
            v1_raw = line_raw[30:40].strip()
            v2_raw = line_raw[40:50].strip()
            v3_raw = line_raw[50:60].strip()

            mid = self.dataframe.parameter[mid_raw[1:]].value if mid_raw.startswith("&") else int(mid_raw)
            rho = self.dataframe.parameter[rho_raw[1:]].value if rho_raw.startswith("&") else float(rho_raw)
            e = self.dataframe.parameter[e_raw[1:]].value if e_raw.startswith("&") else float(e_raw)
            pr = self.dataframe.parameter[pr_raw[1:]].value if pr_raw.startswith("&") else float(pr_raw)

            if len(n_raw) > 0:
                n = self.dataframe.parameter[n_raw[1:]].value if n_raw.startswith("&") else float(n_raw)
            else:
                n = 0.0

            if len(couple_raw) > 0:
                couple = self.dataframe.parameter[couple_raw[1:]].value if couple_raw.startswith("&") else float(couple_raw)
            else:
                couple = 0.0

            if len(m_raw) > 0:
                m = self.dataframe.parameter[m_raw[1:]].value if m_raw.startswith("&") else float(m_raw)
            else:
                m = 0.0

            if len(alias_raw) > 0:
                alias = self.dataframe.parameter[alias_raw[1:]].value if alias_raw.startswith("&") else float(alias_raw)
            else:
                alias = 0.0

            if len(cmo_raw) > 0:
                cmo = self.dataframe.parameter[cmo_raw[1:]].value if cmo_raw.startswith("&") else float(cmo_raw)
            else:
                cmo = 0.0

            if len(con1_raw) > 0:
                con1 = self.dataframe.parameter[con1_raw[1:]].value if con1_raw.startswith("&") else int(con1_raw)
            else:
                con1 = 0

            if len(con2_raw) > 0:
                con2 = self.dataframe.parameter[con2_raw[1:]].value if con2_raw.startswith("&") else int(con2_raw)
            else:
                con2 = 0

            if len(a1_raw) > 0:
                a1 = self.dataframe.parameter[a1_raw[1:]].value if a1_raw.startswith("&") else float(a1_raw)
            else:
                a1 = 0.0

            if len(a2_raw) > 0:
                a2 = self.dataframe.parameter[a2_raw[1:]].value if a2_raw.startswith("&") else float(a2_raw)
            else:
                a2 = 0.0

            if len(a3_raw) > 0:
                a3 = self.dataframe.parameter[a3_raw[1:]].value if a3_raw.startswith("&") else float(a3_raw)
            else:
                a3 = 0.0

            if len(v1_raw) > 0:
                v1 = self.dataframe.parameter[v1_raw[1:]].value if v1_raw.startswith("&") else float(v1_raw)
            else:
                v1 = 0.0

            if len(v2_raw) > 0:
                v2 = self.dataframe.parameter[v2_raw[1:]].value if v2_raw.startswith("&") else float(v2_raw)
            else:
                v2 = 0.0

            if len(v3_raw) > 0:
                v3 = self.dataframe.parameter[v3_raw[1:]].value if v3_raw.startswith("&") else float(v3_raw)
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

