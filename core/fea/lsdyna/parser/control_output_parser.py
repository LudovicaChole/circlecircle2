from core.fea.parser import Parser
from core.fea.model.lsdyna.control_output import ControlOutput


class ControlOutputParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            npopt_raw = line_raw[0:10].strip()
            neecho_raw = line_raw[10:20].strip()
            nrefup_raw = line_raw[20:30].strip()
            iaccop_raw = line_raw[30:40].strip()
            opifs_raw = line_raw[40:50].strip()
            ipnint_raw = line_raw[50:60].strip()
            ikedit_raw = line_raw[60:70].strip()
            iflush_raw = line_raw[70:80].strip()

            self.temp.append(npopt_raw)
            self.temp.append(neecho_raw)
            self.temp.append(nrefup_raw)
            self.temp.append(iaccop_raw)
            self.temp.append(opifs_raw)
            self.temp.append(ipnint_raw)
            self.temp.append(ikedit_raw)
            self.temp.append(iflush_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            npopt_raw = self.temp[0]
            neecho_raw = self.temp[1]
            nrefup_raw = self.temp[2]
            iaccop_raw = self.temp[3]
            opifs_raw = self.temp[4]
            ipnint_raw = self.temp[5]
            ikedit_raw = self.temp[6]
            iflush_raw = self.temp[7]

            iprtf_raw = line_raw[0:10].strip()
            ierode_raw = line_raw[10:20].strip()
            tet10s8_raw = line_raw[20:30].strip()
            msgmax_raw = line_raw[30:40].strip()
            ipcurv_raw = line_raw[40:50].strip()
            gmdt_raw = line_raw[50:60].strip()
            ip1dblt_raw = line_raw[60:70].strip()
            eocs_raw = line_raw[70:80].strip()

            if len(npopt_raw) > 0:
                npopt = self.dataframe.parameter[npopt_raw[1:]].value if npopt_raw.startswith("&") else int(npopt_raw)
            else:
                npopt = 0

            if len(neecho_raw) > 0:
                neecho = self.dataframe.parameter[neecho_raw[1:]].value if neecho_raw.startswith("&") else int(neecho_raw)
            else:
                neecho = 0

            if len(nrefup_raw) > 0:
                nrefup = self.dataframe.parameter[nrefup_raw[1:]].value if nrefup_raw.startswith("&") else int(nrefup_raw)
            else:
                nrefup = 0

            if len(iaccop_raw) > 0:
                iaccop = self.dataframe.parameter[iaccop_raw[1:]].value if iaccop_raw.startswith("&") else int(iaccop_raw)
            else:
                iaccop = 0

            if len(opifs_raw) > 0:
                opifs = self.dataframe.parameter[opifs_raw[1:]].value if opifs_raw.startswith("&") else float(opifs_raw)
            else:
                opifs = 0

            if len(ipnint_raw) > 0:
                ipnint = self.dataframe.parameter[ipnint_raw[1:]].value if ipnint_raw.startswith("&") else int(ipnint_raw)
            else:
                ipnint = 0

            if len(ikedit_raw) > 0:
                ikedit = self.dataframe.parameter[ikedit_raw[1:]].value if ikedit_raw.startswith("&") else int(ikedit_raw)
            else:
                ikedit = 0

            if len(iflush_raw) > 0:
                iflush = self.dataframe.parameter[iflush_raw[1:]].value if iflush_raw.startswith("&") else int(iflush_raw)
            else:
                iflush = 0

            if len(iprtf_raw) > 0:
                iprtf = self.dataframe.parameter[iprtf_raw[1:]].value if iprtf_raw.startswith("&") else int(iprtf_raw)
            else:
                iprtf = 0

            if len(ierode_raw) > 0:
                ierode = self.dataframe.parameter[ierode_raw[1:]].value if ierode_raw.startswith("&") else int(ierode_raw)
            else:
                ierode = 0

            if len(tet10s8_raw) > 0:
                tet10s8 = self.dataframe.parameter[tet10s8_raw[1:]].value if tet10s8_raw.startswith("&") else int(tet10s8_raw)
            else:
                tet10s8 = 0

            if len(msgmax_raw) > 0:
                msgmax = self.dataframe.parameter[msgmax_raw[1:]].value if msgmax_raw.startswith("&") else int(msgmax_raw)
            else:
                msgmax = 0

            if len(ipcurv_raw) > 0:
                ipcurv = self.dataframe.parameter[ipcurv_raw[1:]].value if ipcurv_raw.startswith("&") else int(ipcurv_raw)
            else:
                ipcurv = 0

            if len(gmdt_raw) > 0:
                gmdt = self.dataframe.parameter[gmdt_raw[1:]].value if gmdt_raw.startswith("&") else float(gmdt_raw)
            else:
                gmdt = 0

            if len(ip1dblt_raw) > 0:
                ip1dblt = self.dataframe.parameter[ip1dblt_raw[1:]].value if ip1dblt_raw.startswith("&") else float(
                    ip1dblt_raw)
            else:
                ip1dblt = 0

            if len(eocs_raw) > 0:
                eocs = self.dataframe.parameter[eocs_raw[1:]].value if eocs_raw.startswith("&") else float(eocs_raw)
            else:
                eocs = 0

            uid = len(self.dataframe.control_output) + 1

            self.dataframe.control_output[uid] = ControlOutput(uid=uid,
                                                               npopt=npopt,
                                                               neecho=neecho,
                                                               nrefup=nrefup,
                                                               iaccop=iaccop,
                                                               opifs=opifs,
                                                               ipnint=ipnint,
                                                               ikedit=ikedit,
                                                               iflush=iflush,
                                                               iprtf=iprtf,
                                                               ierode=ierode,
                                                               tet10s8=tet10s8,
                                                               msgmax=msgmax,
                                                               ipcurv=ipcurv,
                                                               gmdt=gmdt,
                                                               ip1dblt=ip1dblt,
                                                               eocs=eocs)

            self.reset()

            return