from core.fea.parser import Parser
from core.fea.model.lsdyna.control_contact import ControlContact


class ControlContactParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            slsfac_raw = line_raw[0:10].strip()
            rwpnal_raw = line_raw[10:20].strip()
            islchk_raw = line_raw[20:30].strip()
            shlthk_raw = line_raw[30:40].strip()
            penopt_raw = line_raw[40:50].strip()
            thkchg_raw = line_raw[50:60].strip()
            orien_raw = line_raw[60:70].strip()
            enmass_raw = line_raw[70:80].strip()

            self.temp.append(slsfac_raw)
            self.temp.append(rwpnal_raw)
            self.temp.append(islchk_raw)
            self.temp.append(shlthk_raw)
            self.temp.append(penopt_raw)
            self.temp.append(thkchg_raw)
            self.temp.append(orien_raw)
            self.temp.append(enmass_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            usrstr_raw = line_raw[0:10].strip()
            usrfrc_raw = line_raw[10:20].strip()
            nsbcs_raw = line_raw[20:30].strip()
            interm_raw = line_raw[30:40].strip()
            xpene_raw = line_raw[40:50].strip()
            ssthk_raw = line_raw[50:60].strip()
            ecdt_raw = line_raw[60:70].strip()
            tiedprj_raw = line_raw[70:80].strip()

            self.temp.append(usrstr_raw)
            self.temp.append(usrfrc_raw)
            self.temp.append(nsbcs_raw)
            self.temp.append(interm_raw)
            self.temp.append(xpene_raw)
            self.temp.append(ssthk_raw)
            self.temp.append(ecdt_raw)
            self.temp.append(tiedprj_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            sfric_raw = line_raw[0:10].strip()
            dfric_raw = line_raw[10:20].strip()
            edc_raw = line_raw[20:30].strip()
            vfc_raw = line_raw[30:40].strip()
            th_raw = line_raw[40:50].strip()
            th_sf_raw = line_raw[50:60].strip()
            pen_sf_raw = line_raw[60:70].strip()
            ptscl_raw = line_raw[70:80].strip()

            self.temp.append(sfric_raw)
            self.temp.append(dfric_raw)
            self.temp.append(edc_raw)
            self.temp.append(vfc_raw)
            self.temp.append(th_raw)
            self.temp.append(th_sf_raw)
            self.temp.append(pen_sf_raw)
            self.temp.append(ptscl_raw)

            self.line_number = 3

            return

        if self.line_number == 3:
            ignore_raw = line_raw[0:10].strip()
            frceng_raw = line_raw[10:20].strip()
            skiprwg_raw = line_raw[20:30].strip()
            outseg_raw = line_raw[30:40].strip()
            spotstp_raw = line_raw[40:50].strip()
            spotdel_raw = line_raw[50:60].strip()
            spothin_raw = line_raw[60:70].strip()

            self.temp.append(ignore_raw)
            self.temp.append(frceng_raw)
            self.temp.append(skiprwg_raw)
            self.temp.append(outseg_raw)
            self.temp.append(spotstp_raw)
            self.temp.append(spotdel_raw)
            self.temp.append(spothin_raw)

            self.line_number = 4

            return

        if self.line_number == 4:
            isym_raw = line_raw[0:10].strip()
            nserod_raw = line_raw[10:20].strip()
            rwgaps_raw = line_raw[20:30].strip()
            rwgdth_raw = line_raw[30:40].strip()
            rwksf_raw = line_raw[40:50].strip()
            icov_raw = line_raw[50:60].strip()
            swradf_raw = line_raw[60:70].strip()
            ithoff_raw = line_raw[70:80].strip()

            self.temp.append(isym_raw)
            self.temp.append(nserod_raw)
            self.temp.append(rwgaps_raw)
            self.temp.append(rwgdth_raw)
            self.temp.append(rwksf_raw)
            self.temp.append(icov_raw)
            self.temp.append(swradf_raw)
            self.temp.append(ithoff_raw)

            self.line_number = 5

            return

        if self.line_number == 5:
            slsfac_raw = self.temp[0]
            rwpnal_raw = self.temp[1]
            islchk_raw = self.temp[2]
            shlthk_raw = self.temp[3]
            penopt_raw = self.temp[4]
            thkchg_raw = self.temp[5]
            orien_raw = self.temp[6]
            enmass_raw = self.temp[7]

            usrstr_raw = self.temp[8]
            usrfrc_raw = self.temp[9]
            nsbcs_raw = self.temp[10]
            interm_raw = self.temp[11]
            xpene_raw = self.temp[12]
            ssthk_raw = self.temp[13]
            ecdt_raw = self.temp[14]
            tiedprj_raw = self.temp[15]

            sfric_raw = self.temp[16]
            dfric_raw = self.temp[17]
            edc_raw = self.temp[18]
            vfc_raw = self.temp[19]
            th_raw = self.temp[20]
            th_sf_raw = self.temp[21]
            pen_sf_raw = self.temp[22]
            ptscl_raw = self.temp[23]

            ignore_raw = self.temp[24]
            frceng_raw = self.temp[25]
            skiprwg_raw = self.temp[26]
            outseg_raw = self.temp[27]
            spotstp_raw = self.temp[28]
            spotdel_raw = self.temp[29]
            spothin_raw = self.temp[30]

            isym_raw = self.temp[31]
            nserod_raw = self.temp[32]
            rwgaps_raw = self.temp[33]
            rwgdth_raw = self.temp[34]
            rwksf_raw = self.temp[35]
            icov_raw = self.temp[36]
            swradf_raw = self.temp[37]
            ithoff_raw = self.temp[38]

            shledg_raw = line_raw[0:10].strip()
            pstiff_raw = line_raw[10:20].strip()
            ithcnt_raw = line_raw[20:30].strip()
            tdcnof_raw = line_raw[30:40].strip()
            ftall_raw = line_raw[40:50].strip()
            shltrw_raw = line_raw[60:70].strip()
            igactc_rwa = line_raw[70:80].strip()

            self.temp.append(shledg_raw)
            self.temp.append(pstiff_raw)
            self.temp.append(ithcnt_raw)
            self.temp.append(tdcnof_raw)
            self.temp.append(ftall_raw)
            self.temp.append(shltrw_raw)
            self.temp.append(igactc_rwa)

            if len(slsfac_raw) > 0:
                slsfac = self.dataframe.parameter[slsfac_raw[1:]].value if slsfac_raw.startswith("&") else float(slsfac_raw)
            else:
                slsfac = 0

            if len(rwpnal_raw) > 0:
                rwpnal = self.dataframe.parameter[rwpnal_raw[1:]].value if rwpnal_raw.startswith("&") else float(rwpnal_raw)
            else:
                rwpnal = 0

            if len(islchk_raw) > 0:
                islchk = self.dataframe.parameter[islchk_raw[1:]].value if islchk_raw.startswith("&") else int(islchk_raw)
            else:
                islchk = 0

            if len(shlthk_raw) > 0:
                shlthk = self.dataframe.parameter[shlthk_raw[1:]].value if shlthk_raw.startswith("&") else int(shlthk_raw)
            else:
                shlthk = 0

            if len(penopt_raw) > 0:
                penopt = self.dataframe.parameter[penopt_raw[1:]].value if penopt_raw.startswith("&") else int(penopt_raw)
            else:
                penopt = 0

            if len(thkchg_raw) > 0:
                thkchg = self.dataframe.parameter[thkchg_raw[1:]].value if thkchg_raw.startswith("&") else int(thkchg_raw)
            else:
                thkchg = 0

            if len(orien_raw) > 0:
                orien = self.dataframe.parameter[orien_raw[1:]].value if orien_raw.startswith("&") else int(orien_raw)
            else:
                orien = 0

            if len(enmass_raw) > 0:
                enmass = self.dataframe.parameter[enmass_raw[1:]].value if enmass_raw.startswith("&") else float(enmass_raw)
            else:
                enmass = 0

            if len(usrstr_raw) > 0:
                usrstr = self.dataframe.parameter[usrstr_raw[1:]].value if usrstr_raw.startswith("&") else float(usrstr_raw)
            else:
                usrstr = 0

            if len(usrfrc_raw) > 0:
                usrfrc = self.dataframe.parameter[usrfrc_raw[1:]].value if usrfrc_raw.startswith("&") else float(usrfrc_raw)
            else:
                usrfrc = 0

            if len(nsbcs_raw) > 0:
                nsbcs = self.dataframe.parameter[nsbcs_raw[1:]].value if nsbcs_raw.startswith("&") else float(nsbcs_raw)
            else:
                nsbcs = 0

            if len(interm_raw) > 0:
                interm = self.dataframe.parameter[interm_raw[1:]].value if interm_raw.startswith("&") else float(interm_raw)
            else:
                interm = 0

            if len(xpene_raw) > 0:
                xpene = self.dataframe.parameter[xpene_raw[1:]].value if xpene_raw.startswith("&") else float(xpene_raw)
            else:
                xpene = 0

            if len(ssthk_raw) > 0:
                ssthk = self.dataframe.parameter[ssthk_raw[1:]].value if ssthk_raw.startswith("&") else int(ssthk_raw)
            else:
                ssthk = 0

            if len(ecdt_raw) > 0:
                ecdt = self.dataframe.parameter[ecdt_raw[1:]].value if ecdt_raw.startswith("&") else float(ecdt_raw)
            else:
                ecdt = 0

            if len(tiedprj_raw) > 0:
                tiedprj = self.dataframe.parameter[tiedprj_raw[1:]].value if tiedprj_raw.startswith("&") else float(
                    tiedprj_raw)
            else:
                tiedprj = 0

            if len(sfric_raw) > 0:
                sfric = self.dataframe.parameter[sfric_raw[1:]].value if sfric_raw.startswith("&") else float(sfric_raw)
            else:
                sfric = 0

            if len(dfric_raw) > 0:
                dfric = self.dataframe.parameter[dfric_raw[1:]].value if dfric_raw.startswith("&") else float(dfric_raw)
            else:
                dfric = 0

            if len(edc_raw) > 0:
                edc = self.dataframe.parameter[edc_raw[1:]].value if edc_raw.startswith("&") else float(edc_raw)
            else:
                edc = 0

            if len(vfc_raw) > 0:
                vfc = self.dataframe.parameter[vfc_raw[1:]].value if vfc_raw.startswith("&") else float(vfc_raw)
            else:
                vfc = 0

            if len(th_raw) > 0:
                th = self.dataframe.parameter[th_raw[1:]].value if th_raw.startswith("&") else float(th_raw)
            else:
                th = 0

            if len(th_sf_raw) > 0:
                th_sf = self.dataframe.parameter[th_sf_raw[1:]].value if th_sf_raw.startswith("&") else float(th_sf_raw)
            else:
                th_sf = 0

            if len(pen_sf_raw) > 0:
                pen_sf = self.dataframe.parameter[pen_sf_raw[1:]].value if pen_sf_raw.startswith("&") else float(pen_sf_raw)
            else:
                pen_sf = 0

            if len(ptscl_raw) > 0:
                ptscl = self.dataframe.parameter[ptscl_raw[1:]].value if ptscl_raw.startswith("&") else float(ptscl_raw)
            else:
                ptscl = 0

            if len(ignore_raw) > 0:
                ignore = self.dataframe.parameter[ignore_raw[1:]].value if ignore_raw.startswith("&") else int(ignore_raw)
            else:
                ignore = 0

            if len(frceng_raw) > 0:
                frceng = self.dataframe.parameter[frceng_raw[1:]].value if frceng_raw.startswith("&") else float(frceng_raw)
            else:
                frceng = 0

            if len(skiprwg_raw) > 0:
                skiprwg = self.dataframe.parameter[skiprwg_raw[1:]].value if skiprwg_raw.startswith("&") else float(
                    skiprwg_raw)
            else:
                skiprwg = 0

            if len(outseg_raw) > 0:
                outseg = self.dataframe.parameter[outseg_raw[1:]].value if outseg_raw.startswith("&") else float(outseg_raw)
            else:
                outseg = 0

            if len(spotstp_raw) > 0:
                spotstp = self.dataframe.parameter[spotstp_raw[1:]].value if spotstp_raw.startswith("&") else float(
                    spotstp_raw)
            else:
                spotstp = 0

            if len(spotdel_raw) > 0:
                spotdel = self.dataframe.parameter[spotdel_raw[1:]].value if spotdel_raw.startswith("&") else float(
                    spotdel_raw)
            else:
                spotdel = 0

            if len(spothin_raw) > 0:
                spothin = self.dataframe.parameter[spothin_raw[1:]].value if spothin_raw.startswith("&") else float(
                    spothin_raw)
            else:
                spothin = 0

            if len(isym_raw) > 0:
                isym = self.dataframe.parameter[isym_raw[1:]].value if isym_raw.startswith("&") else float(isym_raw)
            else:
                isym = 0

            if len(nserod_raw) > 0:
                nserod = self.dataframe.parameter[nserod_raw[1:]].value if nserod_raw.startswith("&") else float(nserod_raw)
            else:
                nserod = 0

            if len(rwgaps_raw) > 0:
                rwgaps = self.dataframe.parameter[rwgaps_raw[1:]].value if rwgaps_raw.startswith("&") else float(rwgaps_raw)
            else:
                rwgaps = 0

            if len(rwgdth_raw) > 0:
                rwgdth = self.dataframe.parameter[rwgdth_raw[1:]].value if rwgdth_raw.startswith("&") else float(rwgdth_raw)
            else:
                rwgdth = 0

            if len(rwksf_raw) > 0:
                rwksf = self.dataframe.parameter[rwksf_raw[1:]].value if rwksf_raw.startswith("&") else float(rwksf_raw)
            else:
                rwksf = 0

            if len(icov_raw) > 0:
                icov = self.dataframe.parameter[icov_raw[1:]].value if icov_raw.startswith("&") else float(icov_raw)
            else:
                icov = 0

            if len(swradf_raw) > 0:
                swradf = self.dataframe.parameter[swradf_raw[1:]].value if swradf_raw.startswith("&") else float(swradf_raw)
            else:
                swradf = 0

            if len(ithoff_raw) > 0:
                ithoff = self.dataframe.parameter[ithoff_raw[1:]].value if ithoff_raw.startswith("&") else float(ithoff_raw)
            else:
                ithoff = 0

            if len(shledg_raw) > 0:
                shledg = self.dataframe.parameter[shledg_raw[1:]].value if shledg_raw.startswith("&") else float(shledg_raw)
            else:
                shledg = 0

            if len(pstiff_raw) > 0:
                pstiff = self.dataframe.parameter[pstiff_raw[1:]].value if pstiff_raw.startswith("&") else float(pstiff_raw)
            else:
                pstiff = 0

            if len(ithcnt_raw) > 0:
                ithcnt = self.dataframe.parameter[ithcnt_raw[1:]].value if ithcnt_raw.startswith("&") else float(ithcnt_raw)
            else:
                ithcnt = 0

            if len(tdcnof_raw) > 0:
                tdcnof = self.dataframe.parameter[tdcnof_raw[1:]].value if tdcnof_raw.startswith("&") else float(tdcnof_raw)
            else:
                tdcnof = 0

            if len(ftall_raw) > 0:
                ftall = self.dataframe.parameter[ftall_raw[1:]].value if ftall_raw.startswith("&") else float(ftall_raw)
            else:
                ftall = 0

            if len(shltrw_raw) > 0:
                shltrw = self.dataframe.parameter[shltrw_raw[1:]].value if shltrw_raw.startswith("&") else float(shltrw_raw)
            else:
                shltrw = 0

            if len(igactc_rwa) > 0:
                igactc = self.dataframe.parameter[igactc_rwa[1:]].value if igactc_rwa.startswith("&") else float(igactc_rwa)
            else:
                igactc = 0

            uid = len(self.dataframe.control_contact) + 1

            self.dataframe.control_contact[uid] = ControlContact(uid=uid,
                                                                 slsfac=slsfac,
                                                                 rwpnal=rwpnal,
                                                                 islchk=islchk,
                                                                 shlthk=shlthk,
                                                                 penopt=penopt,
                                                                 thkchg=thkchg,
                                                                 orien=orien,
                                                                 enmass=enmass,
                                                                 usrstr=usrstr,
                                                                 usrfrc=usrfrc,
                                                                 nsbcs=nsbcs,
                                                                 interm=interm,
                                                                 xpene=xpene,
                                                                 ssthk=ssthk,
                                                                 ecdt=ecdt,
                                                                 tiedprj=tiedprj,
                                                                 sfric=sfric,
                                                                 dfric=dfric,
                                                                 edc=edc,
                                                                 vfc=vfc,
                                                                 th=th,
                                                                 th_sf=th_sf,
                                                                 pen_sf=pen_sf,
                                                                 ptscl=ptscl,
                                                                 ignore=ignore,
                                                                 frceng=frceng,
                                                                 skiprwg=skiprwg,
                                                                 outseg=outseg,
                                                                 spotstp=spotstp,
                                                                 spotdel=spotdel,
                                                                 spothin=spothin,
                                                                 isym=isym,
                                                                 nserod=nserod,
                                                                 rwgaps=rwgaps,
                                                                 rwgdth=rwgdth,
                                                                 rwksf=rwksf,
                                                                 icov=icov,
                                                                 swradf=swradf,
                                                                 ithoff=ithoff,
                                                                 shledg=shledg,
                                                                 pstiff=pstiff,
                                                                 ithcnt=ithcnt,
                                                                 tdcnof=tdcnof,
                                                                 ftall=ftall,
                                                                 shltrw=shltrw,
                                                                 igactc=igactc,
                                                                 )

            self.reset()

            return
