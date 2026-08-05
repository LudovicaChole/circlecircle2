from core.fea.parser import Parser
from core.fea.lsdyna.keywords.mat_add_erosion import MatAddErosion


class MatAddErosionTitleParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            name_raw = line_raw.strip()

            self.temp.append(name_raw)
            self.line_number = 1

            return

        if self.line_number == 1:
            mid_raw = line_raw[0:10].strip()
            excl_raw = line_raw[10:20].strip()
            mxpres_raw = line_raw[20:30].strip()
            mneps_raw = line_raw[30:40].strip()
            effeps_raw = line_raw[40:50].strip()
            voleps_raw = line_raw[50:60].strip()
            numfip_raw = line_raw[60:70].strip()
            ncs_raw = line_raw[70:80].strip()

            self.temp.append(mid_raw)
            self.temp.append(excl_raw)
            self.temp.append(mxpres_raw)
            self.temp.append(mneps_raw)
            self.temp.append(effeps_raw)
            self.temp.append(voleps_raw)
            self.temp.append(numfip_raw)
            self.temp.append(ncs_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            mnpres_raw = line_raw[0:10].strip()
            sigp1_raw = line_raw[10:20].strip()
            sigvm_raw = line_raw[20:30].strip()
            mxeps_raw = line_raw[30:40].strip()
            epssh_raw = line_raw[40:50].strip()
            sigth_raw = line_raw[50:60].strip()
            impulse_raw = line_raw[60:70].strip()
            failtm_raw = line_raw[70:80].strip()

            self.temp.append(mnpres_raw)
            self.temp.append(sigp1_raw)
            self.temp.append(sigvm_raw)
            self.temp.append(mxeps_raw)
            self.temp.append(epssh_raw)
            self.temp.append(sigth_raw)
            self.temp.append(impulse_raw)
            self.temp.append(failtm_raw)

            self.line_number = 3

            return

        if self.line_number == 3:
            idam_raw = line_raw[0:10].strip()
            dmgtyp_raw = line_raw[10:20].strip()
            lcsdg_raw = line_raw[20:30].strip()
            ecrit_raw = line_raw[30:40].strip()
            dmgexp_raw = line_raw[40:50].strip()
            dcrit_raw = line_raw[50:60].strip()
            fadexp_raw = line_raw[60:70].strip()
            lcregd_raw = line_raw[70:80].strip()

            self.temp.append(idam_raw)
            self.temp.append(dmgtyp_raw)
            self.temp.append(lcsdg_raw)
            self.temp.append(ecrit_raw)
            self.temp.append(dmgexp_raw)
            self.temp.append(dcrit_raw)
            self.temp.append(fadexp_raw)
            self.temp.append(lcregd_raw)

            self.line_number = 4

            return

        if self.line_number == 4:
            name_raw = self.temp[0]
            mid_raw = self.temp[1]
            excl_raw = self.temp[2]
            mxpres_raw = self.temp[3]
            mneps_raw = self.temp[4]
            effeps_raw = self.temp[5]
            voleps_raw = self.temp[6]
            numfip_raw = self.temp[7]
            ncs_raw = self.temp[8]
            mnpres_raw = self.temp[9]
            sigp1_raw = self.temp[10]
            sigvm_raw = self.temp[11]
            mxeps_raw = self.temp[12]
            epssh_raw = self.temp[13]
            sigth_raw = self.temp[14]
            impulse_raw = self.temp[15]
            failtm_raw = self.temp[16]
            idam_raw = self.temp[17]
            dmgtyp_raw = self.temp[18]
            lcsdg_raw = self.temp[19]
            ecrit_raw = self.temp[20]
            dmgexp_raw = self.temp[21]
            dcrit_raw = self.temp[22]
            fadexp_raw = self.temp[23]
            lcregd_raw = self.temp[24]

            sizflg_raw = line_raw[0:10].strip()
            refsz_raw = line_raw[10:20].strip()
            nahsv_raw = line_raw[20:30].strip()
            lcsrs_raw = line_raw[30:40].strip()
            shrf_raw = line_raw[40:50].strip()
            biaxf_raw = line_raw[50:60].strip()

            name = name_raw

            if len(mid_raw) > 0:
                mid = self.dataframe.parameter[mid_raw[1:]].value if mid_raw.startswith("&") else int(mid_raw)
            else:
                mid = 0

            if len(excl_raw) > 0:
                excl = self.dataframe.parameter[excl_raw[1:]].value if excl_raw.startswith("&") else float(excl_raw)
            else:
                excl = 0.0

            if len(mxpres_raw) > 0:
                mxpres = self.dataframe.parameter[mxpres_raw[1:]].value if mxpres_raw.startswith("&") else float(
                    mxpres_raw)
            else:
                mxpres = 0.0

            if len(mneps_raw) > 0:
                mneps = self.dataframe.parameter[mneps_raw[1:]].value if mneps_raw.startswith("&") else float(mneps_raw)
            else:
                mneps = 0.0

            if len(effeps_raw) > 0:
                effeps = self.dataframe.parameter[effeps_raw[1:]].value if effeps_raw.startswith("&") else float(
                    effeps_raw)
            else:
                effeps = 0.0

            if len(voleps_raw) > 0:
                voleps = self.dataframe.parameter[voleps_raw[1:]].value if voleps_raw.startswith("&") else float(
                    voleps_raw)
            else:
                voleps = 0.0

            if len(numfip_raw) > 0:
                numfip = self.dataframe.parameter[numfip_raw[1:]].value if numfip_raw.startswith("&") else float(
                    numfip_raw)
            else:
                numfip = 0.0

            if len(ncs_raw) > 0:
                ncs = self.dataframe.parameter[ncs_raw[1:]].value if ncs_raw.startswith("&") else float(ncs_raw)
            else:
                ncs = 0.0

            if len(mnpres_raw) > 0:
                mnpres = self.dataframe.parameter[mnpres_raw[1:]].value if mnpres_raw.startswith("&") else float(
                    mnpres_raw)
            else:
                mnpres = 0.0

            if len(sigp1_raw) > 0:
                sigp1 = self.dataframe.parameter[sigp1_raw[1:]].value if sigp1_raw.startswith("&") else float(sigp1_raw)
            else:
                sigp1 = 0.0

            if len(sigvm_raw) > 0:
                sigvm = self.dataframe.parameter[sigvm_raw[1:]].value if sigvm_raw.startswith("&") else float(sigvm_raw)
            else:
                sigvm = 0.0

            if len(mxeps_raw) > 0:
                mxeps = self.dataframe.parameter[mxeps_raw[1:]].value if mxeps_raw.startswith("&") else float(mxeps_raw)
            else:
                mxeps = 0.0

            if len(epssh_raw) > 0:
                epssh = self.dataframe.parameter[epssh_raw[1:]].value if epssh_raw.startswith("&") else float(epssh_raw)
            else:
                epssh = 0.0

            if len(sigth_raw) > 0:
                sigth = self.dataframe.parameter[sigth_raw[1:]].value if sigth_raw.startswith("&") else float(sigth_raw)
            else:
                sigth = 0.0

            if len(impulse_raw) > 0:
                impulse = self.dataframe.parameter[impulse_raw[1:]].value if impulse_raw.startswith("&") else float(
                    impulse_raw)
            else:
                impulse = 0.0

            if len(failtm_raw) > 0:
                failtm = self.dataframe.parameter[failtm_raw[1:]].value if failtm_raw.startswith("&") else float(
                    failtm_raw)
            else:
                failtm = 0.0

            if len(idam_raw) > 0:
                idam = self.dataframe.parameter[idam_raw[1:]].value if idam_raw.startswith("&") else int(idam_raw)
            else:
                idam = 0.0

            if len(dmgtyp_raw) > 0:
                dmgtyp = self.dataframe.parameter[dmgtyp_raw[1:]].value if dmgtyp_raw.startswith("&") else float(
                    dmgtyp_raw)
            else:
                dmgtyp = 0.0

            if len(lcsdg_raw) > 0:
                lcsdg = self.dataframe.parameter[lcsdg_raw[1:]].value if lcsdg_raw.startswith("&") else int(lcsdg_raw)
            else:
                lcsdg = 0.0

            if len(ecrit_raw) > 0:
                ecrit = self.dataframe.parameter[ecrit_raw[1:]].value if ecrit_raw.startswith("&") else float(ecrit_raw)
            else:
                ecrit = 0.0

            if len(dmgexp_raw) > 0:
                dmgexp = self.dataframe.parameter[dmgexp_raw[1:]].value if dmgexp_raw.startswith("&") else float(
                    dmgexp_raw)
            else:
                dmgexp = 0.0

            if len(dcrit_raw) > 0:
                dcrit = self.dataframe.parameter[dcrit_raw[1:]].value if dcrit_raw.startswith("&") else float(dcrit_raw)
            else:
                dcrit = 0.0

            if len(fadexp_raw) > 0:
                fadexp = self.dataframe.parameter[fadexp_raw[1:]].value if fadexp_raw.startswith("&") else float(
                    fadexp_raw)
            else:
                fadexp = 0.0

            if len(lcregd_raw) > 0:
                lcregd = self.dataframe.parameter[lcregd_raw[1:]].value if lcregd_raw.startswith("&") else int(
                    lcregd_raw)
            else:
                lcregd = 0.0

            if len(sizflg_raw) > 0:
                sizflg = self.dataframe.parameter[sizflg_raw[1:]].value if sizflg_raw.startswith("&") else float(
                    sizflg_raw)
            else:
                sizflg = 0.0

            if len(refsz_raw) > 0:
                refsz = self.dataframe.parameter[refsz_raw[1:]].value if refsz_raw.startswith("&") else float(refsz_raw)
            else:
                refsz = 0.0

            if len(nahsv_raw) > 0:
                nahsv = self.dataframe.parameter[nahsv_raw[1:]].value if nahsv_raw.startswith("&") else float(nahsv_raw)
            else:
                nahsv = 0.0

            if len(lcsrs_raw) > 0:
                lcsrs = self.dataframe.parameter[lcsrs_raw[1:]].value if lcsrs_raw.startswith("&") else float(lcsrs_raw)
            else:
                lcsrs = 0.0

            if len(shrf_raw) > 0:
                shrf = self.dataframe.parameter[shrf_raw[1:]].value if shrf_raw.startswith("&") else float(shrf_raw)
            else:
                shrf = 0.0

            if len(biaxf_raw) > 0:
                biaxf = self.dataframe.parameter[biaxf_raw[1:]].value if biaxf_raw.startswith("&") else float(biaxf_raw)
            else:
                biaxf = 0.0

            self.dataframe.mat_add_erosion[mid] = MatAddErosion(uid=mid,
                                                                excl=excl,
                                                                mxpres=mxpres,
                                                                mneps=mneps,
                                                                effeps=effeps,
                                                                voleps=voleps,
                                                                numfip=numfip,
                                                                ncs=ncs,
                                                                mnpres=mnpres,
                                                                sigp1=sigp1,
                                                                sigvm=sigvm,
                                                                mxeps=mxeps,
                                                                epssh=epssh,
                                                                sigth=sigth,
                                                                impulse=impulse,
                                                                failtm=failtm,
                                                                idam=idam,
                                                                dmgtyp=dmgtyp,
                                                                lcsdg=lcsdg,
                                                                ecrit=ecrit,
                                                                dmgexp=dmgexp,
                                                                dcrit=dcrit,
                                                                fadexp=fadexp,
                                                                lcregd=lcregd,
                                                                sizflg=sizflg,
                                                                refsz=refsz,
                                                                nahsv=nahsv,
                                                                lcsrs=lcsrs,
                                                                shrf=shrf,
                                                                biaxf=biaxf,
                                                                name=name)

            self.reset()

            return


