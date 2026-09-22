from core.fea.parser import Parser
from core.fea.lsdyna.keywords.mat_modified_piecewise_linear_plasticity import MatModifiedPiecewiseLinearPlasticity


class MatModifiedPiecewiseLinearPlasticityParser(Parser):
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
            sigy_raw = line_raw[40:50].strip()
            etan_raw = line_raw[50:60].strip()
            fail_raw = line_raw[60:70].strip()
            tdel_raw = line_raw[70:80].strip()

            self.temp.append(mid_raw)
            self.temp.append(rho_raw)
            self.temp.append(e_raw)
            self.temp.append(pr_raw)
            self.temp.append(sigy_raw)
            self.temp.append(etan_raw)
            self.temp.append(fail_raw)
            self.temp.append(tdel_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            c_raw = line_raw[0:10].strip()
            p_raw = line_raw[10:20].strip()
            lcss_raw = line_raw[20:30].strip()
            lcsr_raw = line_raw[30:40].strip()
            vp_raw = line_raw[40:50].strip()
            epsthin_raw = line_raw[50:60].strip()
            epsmaj_raw = line_raw[60:70].strip()
            numint_raw = line_raw[70:80].strip()

            self.temp.append(c_raw)
            self.temp.append(p_raw)
            self.temp.append(lcss_raw)
            self.temp.append(lcsr_raw)
            self.temp.append(vp_raw)
            self.temp.append(epsthin_raw)
            self.temp.append(epsmaj_raw)
            self.temp.append(numint_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            eps1_raw = line_raw[0:10].strip()
            eps2_raw = line_raw[10:20].strip()
            eps3_raw = line_raw[20:30].strip()
            eps4_raw = line_raw[30:40].strip()
            eps5_raw = line_raw[40:50].strip()
            eps6_raw = line_raw[50:60].strip()
            eps7_raw = line_raw[60:70].strip()
            eps8_raw = line_raw[70:80].strip()

            self.temp.append(eps1_raw)
            self.temp.append(eps2_raw)
            self.temp.append(eps3_raw)
            self.temp.append(eps4_raw)
            self.temp.append(eps5_raw)
            self.temp.append(eps6_raw)
            self.temp.append(eps7_raw)
            self.temp.append(eps8_raw)

            self.line_number = 3

            return

        if self.line_number == 3:
            mid_raw = self.temp[0]
            rho_raw = self.temp[1]
            e_raw = self.temp[2]
            pr_raw = self.temp[3]
            sigy_raw = self.temp[4]
            etan_raw = self.temp[5]
            fail_raw = self.temp[6]
            tdel_raw = self.temp[7]

            c_raw = self.temp[8]
            p_raw = self.temp[9]
            lcss_raw = self.temp[10]
            lcsr_raw = self.temp[11]
            vp_raw = self.temp[12]
            epsthin_raw = self.temp[13]
            epsmaj_raw = self.temp[14]
            numint_raw = self.temp[15]

            eps1_raw = self.temp[16]
            eps2_raw = self.temp[17]
            eps3_raw = self.temp[18]
            eps4_raw = self.temp[19]
            eps5_raw = self.temp[20]
            eps6_raw = self.temp[21]
            eps7_raw = self.temp[22]
            eps8_raw = self.temp[23]

            es1_raw = line_raw[0:10].strip()
            es2_raw = line_raw[10:20].strip()
            es3_raw = line_raw[20:30].strip()
            es4_raw = line_raw[30:40].strip()
            es5_raw = line_raw[40:50].strip()
            es6_raw = line_raw[50:60].strip()
            es7_raw = line_raw[60:70].strip()
            es8_raw = line_raw[70:80].strip()

            mid = self.dataframe.parameter[mid_raw[1:]].value if mid_raw.startswith("&") else int(mid_raw)
            rho = self.dataframe.parameter[rho_raw[1:]].value if rho_raw.startswith("&") else float(rho_raw)
            e = self.dataframe.parameter[e_raw[1:]].value if e_raw.startswith("&") else float(e_raw)
            pr = self.dataframe.parameter[pr_raw[1:]].value if pr_raw.startswith("&") else float(pr_raw)

            if len(sigy_raw) > 0:
                sigy = self.dataframe.parameter[sigy_raw[1:]].value if sigy_raw.startswith("&") else float(sigy_raw)
            else:
                sigy = 0.0

            if len(etan_raw) > 0:
                etan = self.dataframe.parameter[etan_raw[1:]].value if etan_raw.startswith("&") else float(etan_raw)
            else:
                etan = 0.0

            if len(fail_raw) > 0:
                fail = self.dataframe.parameter[fail_raw[1:]].value if fail_raw.startswith("&") else float(fail_raw)
            else:
                fail = 0.0

            if len(tdel_raw) > 0:
                tdel = self.dataframe.parameter[tdel_raw[1:]].value if tdel_raw.startswith("&") else float(tdel_raw)
            else:
                tdel = 0.0

            if len(c_raw) > 0:
                c = self.dataframe.parameter[c_raw[1:]].value if c_raw.startswith("&") else float(c_raw)
            else:
                c = 0.0

            if len(p_raw) > 0:
                p = self.dataframe.parameter[p_raw[1:]].value if p_raw.startswith("&") else float(p_raw)
            else:
                p = 0.0

            if len(lcss_raw) > 0:
                lcss = self.dataframe.parameter[lcss_raw[1:]].value if lcss_raw.startswith("&") else int(lcss_raw)
            else:
                lcss = 0

            if len(lcsr_raw) > 0:
                lcsr = self.dataframe.parameter[lcsr_raw[1:]].value if lcsr_raw.startswith("&") else float(lcsr_raw)
            else:
                lcsr = 0.0

            if len(vp_raw) > 0:
                vp = self.dataframe.parameter[vp_raw[1:]].value if vp_raw.startswith("&") else float(vp_raw)
            else:
                vp = 0.0

            if len(epsthin_raw) > 0:
                epsthin = self.dataframe.parameter[epsthin_raw[1:]].value if epsthin_raw.startswith("&") else float(epsthin_raw)
            else:
                epsthin = 0.0

            if len(epsmaj_raw) > 0:
                epsmaj = self.dataframe.parameter[epsmaj_raw[1:]].value if epsmaj_raw.startswith("&") else float(epsmaj_raw)
            else:
                epsmaj = 0.0

            if len(numint_raw) > 0:
                numint = self.dataframe.parameter[numint_raw[1:]].value if numint_raw.startswith("&") else float(numint_raw)
            else:
                numint = 0.0

            if len(eps1_raw) > 0:
                eps1 = self.dataframe.parameter[eps1_raw[1:]].value if eps1_raw.startswith("&") else float(eps1_raw)
            else:
                eps1 = 0.0

            if len(eps2_raw) > 0:
                eps2 = self.dataframe.parameter[eps2_raw[1:]].value if eps2_raw.startswith("&") else float(eps2_raw)
            else:
                eps2 = 0.0

            if len(eps3_raw) > 0:
                eps3 = self.dataframe.parameter[eps3_raw[1:]].value if eps3_raw.startswith("&") else float(eps3_raw)
            else:
                eps3 = 0.0

            if len(eps4_raw) > 0:
                eps4 = self.dataframe.parameter[eps4_raw[1:]].value if eps4_raw.startswith("&") else float(eps4_raw)
            else:
                eps4 = 0.0

            if len(eps5_raw) > 0:
                eps5 = self.dataframe.parameter[eps5_raw[1:]].value if eps5_raw.startswith("&") else float(eps5_raw)
            else:
                eps5 = 0.0

            if len(eps6_raw) > 0:
                eps6 = self.dataframe.parameter[eps6_raw[1:]].value if eps6_raw.startswith("&") else float(eps6_raw)
            else:
                eps6 = 0.0

            if len(eps7_raw) > 0:
                eps7 = self.dataframe.parameter[eps7_raw[1:]].value if eps7_raw.startswith("&") else float(eps7_raw)
            else:
                eps7 = 0.0

            if len(eps8_raw) > 0:
                eps8 = self.dataframe.parameter[eps8_raw[1:]].value if eps8_raw.startswith("&") else float(eps8_raw)
            else:
                eps8 = 0.0

            if len(es1_raw) > 0:
                es1 = self.dataframe.parameter[es1_raw[1:]].value if es1_raw.startswith("&") else float(es1_raw)
            else:
                es1 = 0.0

            if len(es2_raw) > 0:
                es2 = self.dataframe.parameter[es2_raw[1:]].value if es2_raw.startswith("&") else float(es2_raw)
            else:
                es2 = 0.0

            if len(es3_raw) > 0:
                es3 = self.dataframe.parameter[es3_raw[1:]].value if es3_raw.startswith("&") else float(es3_raw)
            else:
                es3 = 0.0

            if len(es4_raw) > 0:
                es4 = self.dataframe.parameter[es4_raw[1:]].value if es4_raw.startswith("&") else float(es4_raw)
            else:
                es4 = 0.0

            if len(es5_raw) > 0:
                es5 = self.dataframe.parameter[es5_raw[1:]].value if es5_raw.startswith("&") else float(es5_raw)
            else:
                es5 = 0.0

            if len(es6_raw) > 0:
                es6 = self.dataframe.parameter[es6_raw[1:]].value if es6_raw.startswith("&") else float(es6_raw)
            else:
                es6 = 0.0

            if len(es7_raw) > 0:
                es7 = self.dataframe.parameter[es7_raw[1:]].value if es7_raw.startswith("&") else float(es7_raw)
            else:
                es7 = 0.0

            if len(es8_raw) > 0:
                es8 = self.dataframe.parameter[es8_raw[1:]].value if es8_raw.startswith("&") else float(es8_raw)
            else:
                es8 = 0.0

            self.dataframe.material[mid] = MatModifiedPiecewiseLinearPlasticity(uid=mid,
                                                                                rho=rho,
                                                                                e=e,
                                                                                pr=pr,
                                                                                sigy=sigy,
                                                                                etan=etan,
                                                                                fail=fail,
                                                                                tdel=tdel,
                                                                                c=c,
                                                                                p=p,
                                                                                lcss=lcss,
                                                                                lcsr=lcsr,
                                                                                vp=vp,
                                                                                epsthin=epsthin,
                                                                                epsmaj=epsmaj,
                                                                                numint=numint,
                                                                                eps1=eps1,
                                                                                eps2=eps2,
                                                                                eps3=eps3,
                                                                                eps4=eps4,
                                                                                eps5=eps5,
                                                                                eps6=eps6,
                                                                                eps7=eps7,
                                                                                eps8=eps8,
                                                                                es1=es1,
                                                                                es2=es2,
                                                                                es3=es3,
                                                                                es4=es4,
                                                                                es5=es5,
                                                                                es6=es6,
                                                                                es7=es7,
                                                                                es8=es8)

            self.dataframe.storge_material_id.append(mid)

            self.reset()

            return

