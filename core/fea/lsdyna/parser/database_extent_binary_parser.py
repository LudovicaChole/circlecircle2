from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.parser import Parser
from core.fea.model.lsdyna.database_extent_binary import DatabaseExtentBinary


class DatabaseExtentBinaryParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            neiph_raw = fields(line_raw)[0]
            neips_raw = fields(line_raw)[1]
            maxint_raw = fields(line_raw)[2]
            strflg_raw = fields(line_raw)[3]
            sigflg_raw = fields(line_raw)[4]
            epsflg_raw = fields(line_raw)[5]
            rltflg_raw = fields(line_raw)[6]
            engflg_raw = fields(line_raw)[7]

            self.temp.append(neiph_raw)
            self.temp.append(neips_raw)
            self.temp.append(maxint_raw)
            self.temp.append(strflg_raw)
            self.temp.append(sigflg_raw)
            self.temp.append(epsflg_raw)
            self.temp.append(rltflg_raw)
            self.temp.append(engflg_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            neiph_raw = self.temp[0]
            neips_raw = self.temp[1]
            maxint_raw = self.temp[2]
            strflg_raw = self.temp[3]
            sigflg_raw = self.temp[4]
            epsflg_raw = self.temp[5]
            rltflg_raw = self.temp[6]
            engflg_raw = self.temp[7]

            cmpflg_raw = fields(line_raw)[0]
            ieverp_raw = fields(line_raw)[1]
            beamip_raw = fields(line_raw)[2]
            dcomp_raw = fields(line_raw)[3]
            shge_raw = fields(line_raw)[4]
            stssz_raw = fields(line_raw)[5]
            n3thdt_raw = fields(line_raw)[6]
            ialemat_raw = fields(line_raw)[7]

            if len(neiph_raw) > 0:
                neiph = number(neiph_raw, self.dataframe, integer=False)
            else:
                neiph = 0

            if len(neips_raw) > 0:
                neips = number(neips_raw, self.dataframe, integer=False)
            else:
                neips = 0

            if len(maxint_raw) > 0:
                maxint = number(maxint_raw, self.dataframe, integer=False)
            else:
                maxint = 0

            if len(strflg_raw) > 0:
                strflg = number(strflg_raw, self.dataframe, integer=False)
            else:
                strflg = 0

            if len(sigflg_raw) > 0:
                sigflg = number(sigflg_raw, self.dataframe, integer=False)
            else:
                sigflg = 0

            if len(epsflg_raw) > 0:
                epsflg = number(epsflg_raw, self.dataframe, integer=False)
            else:
                epsflg = 0

            if len(rltflg_raw) > 0:
                rltflg = number(rltflg_raw, self.dataframe, integer=False)
            else:
                rltflg = 0

            if len(engflg_raw) > 0:
                engflg = self.dataframe.parameter[engflg_raw[1:0]] if engflg_raw.startswith("&") else float(engflg_raw)
            else:
                engflg = 0

            if len(cmpflg_raw) > 0:
                cmpflg = number(cmpflg_raw, self.dataframe, integer=False)
            else:
                cmpflg = 0

            if len(ieverp_raw) > 0:
                ieverp = number(ieverp_raw, self.dataframe, integer=False)
            else:
                ieverp = 0

            if len(beamip_raw) > 0:
                beamip = number(beamip_raw, self.dataframe, integer=False)
            else:
                beamip = 0

            if len(dcomp_raw) > 0:
                dcomp = number(dcomp_raw, self.dataframe, integer=False)
            else:
                dcomp = 0

            if len(shge_raw) > 0:
                shge = number(shge_raw, self.dataframe, integer=False)
            else:
                shge = 0

            if len(stssz_raw) > 0:
                stssz = number(stssz_raw, self.dataframe, integer=False)
            else:
                stssz = 0

            if len(n3thdt_raw) > 0:
                n3thdt = number(n3thdt_raw, self.dataframe, integer=False)
            else:
                n3thdt = 0

            if len(ialemat_raw) > 0:
                ialemat = number(ialemat_raw, self.dataframe, integer=False)
            else:
                ialemat = 0

            uid = len(self.dataframe.database_extent_binary) + 1

            self.dataframe.database_extent_binary[uid] = DatabaseExtentBinary(uid=uid,
                                                                              neiph=neiph,
                                                                              neips=neips,
                                                                              maxint=maxint,
                                                                              strflg=strflg,
                                                                              sigflg=sigflg,
                                                                              epsflg=epsflg,
                                                                              rltflg=rltflg,
                                                                              engflg=engflg,
                                                                              cmpflg=cmpflg,
                                                                              ieverp=ieverp,
                                                                              beamip=beamip,
                                                                              dcomp=dcomp,
                                                                              shge=shge,
                                                                              stssz=stssz,
                                                                              n3thdt=n3thdt,
                                                                              ialemat=ialemat)

            self.reset()

            return