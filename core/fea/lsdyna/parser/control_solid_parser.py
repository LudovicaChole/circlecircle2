from core.fea.parser import Parser
from core.fea.model.lsdyna.control_solid import ControlSolid


class ControlSolidParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            esort_raw = line_raw[0:10].strip()
            fmatrx_raw = line_raw[10:20].strip()
            niptets_raw = line_raw[20:30].strip()
            swlocl_raw = line_raw[30:40].strip()
            psfail_raw = line_raw[40:50].strip()
            t10jtol_raw = line_raw[50:60].strip()
            icoh_raw = line_raw[60:70].strip()
            tet13k_raw = line_raw[70:80].strip()

            self.temp.append(esort_raw)
            self.temp.append(fmatrx_raw)
            self.temp.append(niptets_raw)
            self.temp.append(swlocl_raw)
            self.temp.append(psfail_raw)
            self.temp.append(t10jtol_raw)
            self.temp.append(icoh_raw)
            self.temp.append(tet13k_raw)
            self.temp.append(line_raw[80:90])

            self.line_number = 1

            return

        if self.line_number == 1:
            esort_raw = self.temp[0]
            fmatrx_raw = self.temp[1]
            niptets_raw = self.temp[2]
            swlocl_raw = self.temp[3]
            psfail_raw = self.temp[4]
            t10jtol_raw = self.temp[5]
            icoh_raw = self.temp[6]
            tet13k_raw = self.temp[7]

            pm1_raw = line_raw[0:8].strip()
            pm2_raw = line_raw[8:16].strip()
            pm3_raw = line_raw[16:24].strip()
            pm4_raw = line_raw[24:32].strip()
            pm5_raw = line_raw[32:40].strip()
            pm6_raw = line_raw[40:48].strip()
            pm7_raw = line_raw[48:56].strip()
            pm8_raw = line_raw[56:64].strip()
            pm9_raw = line_raw[64:72].strip()
            pm10_raw = line_raw[72:80].strip()

            if len(esort_raw) > 0:
                esort = self.dataframe.parameter[esort_raw[1:]].value if esort_raw.startswith("&") else int(esort_raw)
            else:
                esort = 0

            if len(fmatrx_raw) > 0:
                fmatrx = self.dataframe.parameter[fmatrx_raw[1:]].value if fmatrx_raw.startswith("&") else float(fmatrx_raw)
            else:
                fmatrx = 0

            if len(niptets_raw) > 0:
                niptets = self.dataframe.parameter[niptets_raw[1:]].value if niptets_raw.startswith("&") else float(
                    niptets_raw)
            else:
                niptets = 0

            if len(swlocl_raw) > 0:
                swlocl = self.dataframe.parameter[swlocl_raw[1:]].value if swlocl_raw.startswith("&") else float(swlocl_raw)
            else:
                swlocl = 0

            if len(psfail_raw) > 0:
                psfail = self.dataframe.parameter[psfail_raw[1:]].value if psfail_raw.startswith("&") else float(psfail_raw)
            else:
                psfail = 0

            if len(t10jtol_raw) > 0:
                t10jtol = self.dataframe.parameter[t10jtol_raw[1:]].value if t10jtol_raw.startswith("&") else float(
                    t10jtol_raw)
            else:
                t10jtol = 0

            if len(icoh_raw) > 0:
                icoh = self.dataframe.parameter[icoh_raw[1:]].value if icoh_raw.startswith("&") else float(icoh_raw)
            else:
                icoh = 0

            if len(tet13k_raw) > 0:
                tet13k = self.dataframe.parameter[tet13k_raw[1:]].value if tet13k_raw.startswith("&") else float(tet13k_raw)
            else:
                tet13k = 0

            if len(pm1_raw) > 0:
                pm1 = self.dataframe.parameter[pm1_raw[1:]].value if pm1_raw.startswith("&") else float(pm1_raw)
            else:
                pm1 = 0

            if len(pm2_raw) > 0:
                pm2 = self.dataframe.parameter[pm2_raw[1:]].value if pm2_raw.startswith("&") else float(pm2_raw)
            else:
                pm2 = 0

            if len(pm3_raw) > 0:
                pm3 = self.dataframe.parameter[pm3_raw[1:]].value if pm3_raw.startswith("&") else float(pm3_raw)
            else:
                pm3 = 0

            if len(pm4_raw) > 0:
                pm4 = self.dataframe.parameter[pm4_raw[1:]].value if pm4_raw.startswith("&") else float(pm4_raw)
            else:
                pm4 = 0

            if len(pm5_raw) > 0:
                pm5 = self.dataframe.parameter[pm5_raw[1:]].value if pm5_raw.startswith("&") else float(pm5_raw)
            else:
                pm5 = 0

            if len(pm6_raw) > 0:
                pm6 = self.dataframe.parameter[pm6_raw[1:]].value if pm6_raw.startswith("&") else float(pm6_raw)
            else:
                pm6 = 0

            if len(pm7_raw) > 0:
                pm7 = self.dataframe.parameter[pm7_raw[1:]].value if pm7_raw.startswith("&") else float(pm7_raw)
            else:
                pm7 = 0

            if len(pm8_raw) > 0:
                pm8 = self.dataframe.parameter[pm8_raw[1:]].value if pm8_raw.startswith("&") else float(pm8_raw)
            else:
                pm8 = 0

            if len(pm9_raw) > 0:
                pm9 = self.dataframe.parameter[pm9_raw[1:]].value if pm9_raw.startswith("&") else float(pm9_raw)
            else:
                pm9 = 0

            if len(pm10_raw) > 0:
                pm10 = self.dataframe.parameter[pm10_raw[1:]].value if pm10_raw.startswith("&") else float(pm10_raw)
            else:
                pm10 = 0

            uid = len(self.dataframe.control_solid) + 1

            self.dataframe.control_solid[uid] = ControlSolid(uid=uid,
                                                             esort=esort,
                                                             fmatrx=fmatrx,
                                                             niptets=niptets,
                                                             swlocl=swlocl,
                                                             psfail=psfail,
                                                             t10jtol=t10jtol,
                                                             icoh=icoh,
                                                             tet13k=tet13k,
                                                             pm1=pm1,
                                                             pm2=pm2,
                                                             pm3=pm3,
                                                             pm4=pm4,
                                                             pm5=pm5,
                                                             pm6=pm6,
                                                             pm7=pm7,
                                                             pm8=pm8,
                                                             pm9=pm9,
                                                             pm10=pm10)

            self.reset()

            return