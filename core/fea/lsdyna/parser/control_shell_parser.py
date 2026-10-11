from core.fea.parser import Parser
from core.fea.model.lsdyna.control_shell import ControlShell


class ControlShellParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            warpang_raw = line_raw[0:10].strip()
            esort_raw = line_raw[10:20].strip()
            irnxx_raw = line_raw[20:30].strip()
            istupd_raw = line_raw[30:40].strip()
            theory_raw = line_raw[40:50].strip()
            bwc_raw = line_raw[50:60].strip()
            miter_raw = line_raw[60:70].strip()
            proj_raw = line_raw[70:80].strip()

            self.temp.append(warpang_raw)
            self.temp.append(esort_raw)
            self.temp.append(irnxx_raw)
            self.temp.append(istupd_raw)
            self.temp.append(theory_raw)
            self.temp.append(bwc_raw)
            self.temp.append(miter_raw)
            self.temp.append(proj_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            rotascl_raw = line_raw[0:10].strip()
            intgrd_raw = line_raw[10:20].strip()
            lamsht_raw = line_raw[20:30].strip()
            cstyp6_raw = line_raw[30:40].strip()
            thshell_raw = line_raw[40:50].strip()

            self.temp.append(rotascl_raw)
            self.temp.append(intgrd_raw)
            self.temp.append(lamsht_raw)
            self.temp.append(cstyp6_raw)
            self.temp.append(thshell_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            pstupd_raw = line_raw[0:10].strip()
            sidt4tu_raw = line_raw[10:20].strip()
            cntco_raw = line_raw[20:30].strip()
            itsflg_raw = line_raw[30:40].strip()
            irquad_raw = line_raw[40:50].strip()
            w_mode_raw = line_raw[50:60].strip()
            stretch_raw = line_raw[60:70].strip()
            icrq_raw = line_raw[70:80].strip()

            self.temp.append(pstupd_raw)
            self.temp.append(sidt4tu_raw)
            self.temp.append(cntco_raw)
            self.temp.append(itsflg_raw)
            self.temp.append(irquad_raw)
            self.temp.append(w_mode_raw)
            self.temp.append(stretch_raw)
            self.temp.append(icrq_raw)

            self.line_number = 3

            return

        if self.line_number == 3:
            warpang_raw = self.temp[0]
            esort_raw = self.temp[1]
            irnxx_raw = self.temp[2]
            istupd_raw = self.temp[3]
            theory_raw = self.temp[4]
            bwc_raw = self.temp[5]
            miter_raw = self.temp[6]
            proj_raw = self.temp[7]
            rotascl_raw = self.temp[8]
            intgrd_raw = self.temp[9]
            lamsht_raw = self.temp[10]
            cstyp6_raw = self.temp[11]
            thshell_raw = self.temp[12]
            pstupd_raw = self.temp[13]
            sidt4tu_raw = self.temp[14]
            cntco_raw = self.temp[15]
            itsflg_raw = self.temp[16]
            irquad_raw = self.temp[17]
            w_mode_raw = self.temp[18]
            stretch_raw = self.temp[19]
            icrq_raw = self.temp[20]

            nfail1_raw = line_raw[0:10].strip()
            nfail4_raw = line_raw[10:20].strip()
            psnfail_raw = line_raw[20:30].strip()
            keepcs_raw = line_raw[30:40].strip()
            delfr_raw = line_raw[40:50].strip()
            drcpsid_raw = line_raw[50:60].strip()
            drcprm_raw = line_raw[60:70].strip()
            intperr_raw = line_raw[70:80].strip()

            if len(warpang_raw) > 0:
                warpang = self.dataframe.parameter[warpang_raw[1:]].value if warpang_raw.startswith("&") else float(
                    warpang_raw)
            else:
                warpang = 0

            if len(esort_raw) > 0:
                esort = self.dataframe.parameter[esort_raw[1:]].value if esort_raw.startswith("&") else int(esort_raw)
            else:
                esort = 0

            if len(irnxx_raw) > 0:
                irnxx = self.dataframe.parameter[irnxx_raw[1:]].value if irnxx_raw.startswith("&") else int(irnxx_raw)
            else:
                irnxx = 0

            if len(istupd_raw) > 0:
                istupd = self.dataframe.parameter[istupd_raw[1:]].value if istupd_raw.startswith("&") else int(istupd_raw)
            else:
                istupd = 0

            if len(theory_raw) > 0:
                theory = self.dataframe.parameter[theory_raw[1:]].value if theory_raw.startswith("&") else int(theory_raw)
            else:
                theory = 0

            if len(bwc_raw) > 0:
                bwc = self.dataframe.parameter[bwc_raw[1:]].value if bwc_raw.startswith("&") else int(bwc_raw)
            else:
                bwc = 0

            if len(miter_raw) > 0:
                miter = self.dataframe.parameter[miter_raw[1:]].value if miter_raw.startswith("&") else int(miter_raw)
            else:
                miter = 0

            if len(proj_raw) > 0:
                proj = self.dataframe.parameter[proj_raw[1:]].value if proj_raw.startswith("&") else int(proj_raw)
            else:
                proj = 0

            if len(rotascl_raw) > 0:
                rotascl = self.dataframe.parameter[rotascl_raw[1:]].value if rotascl_raw.startswith("&") else float(
                    rotascl_raw)
            else:
                rotascl = 0

            if len(intgrd_raw) > 0:
                intgrd = self.dataframe.parameter[intgrd_raw[1:]].value if intgrd_raw.startswith("&") else float(intgrd_raw)
            else:
                intgrd = 0

            if len(lamsht_raw) > 0:
                lamsht = self.dataframe.parameter[lamsht_raw[1:]].value if lamsht_raw.startswith("&") else float(lamsht_raw)
            else:
                lamsht = 0

            if len(cstyp6_raw) > 0:
                cstyp6 = self.dataframe.parameter[cstyp6_raw[1:]].value if cstyp6_raw.startswith("&") else float(cstyp6_raw)
            else:
                cstyp6 = 0

            if len(thshell_raw) > 0:
                thshell = self.dataframe.parameter[thshell_raw[1:]].value if thshell_raw.startswith("&") else float(
                    thshell_raw)
            else:
                thshell = 0

            if len(pstupd_raw) > 0:
                pstupd = self.dataframe.parameter[pstupd_raw[1:]].value if pstupd_raw.startswith("&") else int(pstupd_raw)
            else:
                pstupd = 0

            if len(sidt4tu_raw) > 0:
                sidt4tu = self.dataframe.parameter[sidt4tu_raw[1:]].value if sidt4tu_raw.startswith("&") else float(
                    sidt4tu_raw)
            else:
                sidt4tu = 0

            if len(cntco_raw) > 0:
                cntco = self.dataframe.parameter[cntco_raw[1:]].value if cntco_raw.startswith("&") else float(cntco_raw)
            else:
                cntco = 0

            if len(itsflg_raw) > 0:
                itsflg = self.dataframe.parameter[itsflg_raw[1:]].value if itsflg_raw.startswith("&") else float(itsflg_raw)
            else:
                itsflg = 0

            if len(irquad_raw) > 0:
                irquad = self.dataframe.parameter[irquad_raw[1:]].value if irquad_raw.startswith("&") else int(irquad_raw)
            else:
                irquad = 0

            if len(w_mode_raw) > 0:
                w_mode = self.dataframe.parameter[w_mode_raw[1:]].value if w_mode_raw.startswith("&") else float(w_mode_raw)
            else:
                w_mode = 0

            if len(stretch_raw) > 0:
                stretch = self.dataframe.parameter[stretch_raw[1:]].value if stretch_raw.startswith("&") else float(
                    stretch_raw)
            else:
                stretch = 0

            if len(icrq_raw) > 0:
                icrq = self.dataframe.parameter[icrq_raw[1:]].value if icrq_raw.startswith("&") else float(icrq_raw)
            else:
                icrq = 0

            if len(nfail1_raw) > 0:
                nfail1 = self.dataframe.parameter[nfail1_raw[1:]].value if nfail1_raw.startswith("&") else int(nfail1_raw)
            else:
                nfail1 = 0

            if len(nfail4_raw) > 0:
                nfail4 = self.dataframe.parameter[nfail4_raw[1:]].value if nfail4_raw.startswith("&") else int(nfail4_raw)
            else:
                nfail4 = 0

            if len(psnfail_raw) > 0:
                psnfail = self.dataframe.parameter[psnfail_raw[1:]].value if psnfail_raw.startswith("&") else float(psnfail_raw)
            else:
                psnfail = 0

            if len(keepcs_raw) > 0:
                keepcs = self.dataframe.parameter[keepcs_raw[1:]].value if keepcs_raw.startswith("&") else int(keepcs_raw)
            else:
                keepcs = 0

            if len(delfr_raw) > 0:
                delfr = self.dataframe.parameter[delfr_raw[1:]].value if delfr_raw.startswith("&") else int(delfr_raw)
            else:
                delfr = 0

            if len(drcpsid_raw) > 0:
                drcpsid = self.dataframe.parameter[drcpsid_raw[1:]].value if drcpsid_raw.startswith("&") else int(drcpsid_raw)
            else:
                drcpsid = 0

            if len(drcprm_raw) > 0:
                drcprm = self.dataframe.parameter[drcprm_raw[1:]].value if drcprm_raw.startswith("&") else float(drcprm_raw)
            else:
                drcprm = 0

            if len(intperr_raw) > 0:
                intperr = self.dataframe.parameter[intperr_raw[1:]].value if intperr_raw.startswith("&") else int(intperr_raw)
            else:
                intperr = 0

            uid = len(self.dataframe.control_shell) + 1

            self.dataframe.control_shell[uid] = ControlShell(uid=uid,
                                                             wrpang=warpang,
                                                             esort=esort,
                                                             irnxx=irnxx,
                                                             istupd=istupd,
                                                             theory=theory,
                                                             bwc=bwc,
                                                             miter=miter,
                                                             proj=proj,
                                                             rotascl=rotascl,
                                                             intgrd=intgrd,
                                                             lamsht=lamsht,
                                                             cstyp6=cstyp6,
                                                             thshell=thshell,
                                                             pstupd=pstupd,
                                                             sidt4tu=sidt4tu,
                                                             cntco=cntco,
                                                             itsflg=itsflg,
                                                             irquad=irquad,
                                                             w_mode=w_mode,
                                                             stretch=stretch,
                                                             icrq=icrq,
                                                             nfail1=nfail1,
                                                             nfail4=nfail4,
                                                             psnfail=psnfail,
                                                             keepcs=keepcs,
                                                             delfr=delfr,
                                                             drcpsid=drcpsid,
                                                             drcprm=drcprm,
                                                             intperr=intperr)

            self.reset()

            return
