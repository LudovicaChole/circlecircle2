from core.fea.parser import Parser
from core.fea.model.lsdyna.part import Part


class PartInertiaParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            name_raw = line_raw.strip()
            self.temp.append(name_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            pid_raw = line_raw[0:10].strip()
            secid_raw = line_raw[10:20].strip()
            mid_raw = line_raw[20:30].strip()
            eosid_raw = line_raw[30:40].strip()
            hgid_raw = line_raw[40:50].strip()
            grav_raw = line_raw[50:60].strip()
            adpopt_raw = line_raw[60:70].strip()
            tmid_raw = line_raw[70:80].strip()

            self.temp.append(pid_raw)
            self.temp.append(secid_raw)
            self.temp.append(mid_raw)
            self.temp.append(eosid_raw)
            self.temp.append(hgid_raw)
            self.temp.append(grav_raw)
            self.temp.append(adpopt_raw)
            self.temp.append(tmid_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            xc_raw = line_raw[0:10].strip()
            yc_raw = line_raw[10:20].strip()
            zc_raw = line_raw[20:30].strip()
            tm_raw = line_raw[30:40].strip()
            ircs_raw = line_raw[40:50].strip()
            nodeid_raw = line_raw[50:60].strip()

            self.temp.append(xc_raw)
            self.temp.append(yc_raw)
            self.temp.append(zc_raw)
            self.temp.append(tm_raw)
            self.temp.append(ircs_raw)
            self.temp.append(nodeid_raw)

            self.line_number = 3

            return

        if self.line_number == 3:
            ixx_raw = line_raw[0:10].strip()
            ixy_raw = line_raw[10:20].strip()
            ixz_raw = line_raw[20:30].strip()
            iyy_raw = line_raw[30:40].strip()
            iyz_raw = line_raw[40:50].strip()
            izz_raw = line_raw[50:60].strip()

            self.temp.append(ixx_raw)
            self.temp.append(ixy_raw)
            self.temp.append(ixz_raw)
            self.temp.append(iyy_raw)
            self.temp.append(iyz_raw)
            self.temp.append(izz_raw)

            self.line_number = 4

            return

        if self.line_number == 4:
            name_raw = self.temp[0]
            pid_raw = self.temp[1]
            secid_raw = self.temp[2]
            mid_raw = self.temp[3]
            eosid_raw = self.temp[4]
            hgid_raw = self.temp[5]
            grav_raw = self.temp[6]
            adpopt_raw = self.temp[7]
            tmid_raw = self.temp[8]
            xc_raw = self.temp[9]
            yc_raw = self.temp[10]
            zc_raw = self.temp[11]
            tm_raw = self.temp[12]
            ircs_raw = self.temp[13]
            nodeid_raw = self.temp[14]
            ixx_raw = self.temp[15]
            ixy_raw = self.temp[16]
            ixz_raw = self.temp[17]
            iyy_raw = self.temp[18]
            iyz_raw = self.temp[19]
            izz_raw = self.temp[20]

            vtx_raw = line_raw[0:10].strip()
            vty_raw = line_raw[10:20].strip()
            vtz_raw = line_raw[20:30].strip()
            vrx_raw = line_raw[30:40].strip()
            vry_raw = line_raw[40:50].strip()
            vrz_raw = line_raw[50:60].strip()

            name = name_raw

            if len(pid_raw) > 0:
                pid = self.dataframe.parameter[pid_raw[1:]].value if pid_raw.startswith("&") else int(pid_raw)
            else:
                pid = 0

            if len(secid_raw) > 0:
                secid = self.dataframe.parameter[secid_raw[1:]].value if secid_raw.startswith("&") else int(secid_raw)
            else:
                secid = 0

            if len(mid_raw) > 0:
                mid = self.dataframe.parameter[mid_raw[1:]].value if mid_raw.startswith("&") else int(mid_raw)
            else:
                mid = 0

            if len(eosid_raw) > 0:
                eosid = self.dataframe.parameter[eosid_raw[1:]].value if eosid_raw.startswith("&") else int(eosid_raw)
            else:
                eosid = 0

            if len(hgid_raw) > 0:
                hgid = self.dataframe.parameter[hgid_raw[1:]].value if hgid_raw.startswith("&") else int(hgid_raw)
            else:
                hgid = 0

            if len(grav_raw) > 0:
                grav = self.dataframe.parameter[grav_raw[1:]].value if grav_raw.startswith("&") else float(grav_raw)
            else:
                grav = 0.0

            if len(adpopt_raw) > 0:
                adpopt = self.dataframe.parameter[adpopt_raw[1:]].value if adpopt_raw.startswith("&") else float(adpopt_raw)
            else:
                adpopt = 0.0

            if len(tmid_raw) > 0:
                tmid = self.dataframe.parameter[tmid_raw[1:]].value if tmid_raw.startswith("&") else int(tmid_raw)
            else:
                tmid = 0

            if len(xc_raw) > 0:
                xc = self.dataframe.parameter[xc_raw[1:]].value if xc_raw.startswith("&") else float(xc_raw)
            else:
                xc = 0.0

            if len(yc_raw) > 0:
                yc = self.dataframe.parameter[yc_raw[1:]].value if yc_raw.startswith("&") else float(yc_raw)
            else:
                yc = 0.0

            if len(zc_raw) > 0:
                zc = self.dataframe.parameter[zc_raw[1:]].value if zc_raw.startswith("&") else float(zc_raw)
            else:
                zc = 0.0

            if len(tm_raw) > 0:
                tm = self.dataframe.parameter[tm_raw[1:]].value if tm_raw.startswith("&") else float(tm_raw)
            else:
                tm = 0.0

            if len(ircs_raw) > 0:
                ircs = self.dataframe.parameter[ircs_raw[1:]].value if ircs_raw.startswith("&") else float(ircs_raw)
            else:
                ircs = 0.0

            if len(nodeid_raw) > 0:
                nodeid = self.dataframe.parameter[nodeid_raw[1:]].value if nodeid_raw.startswith("&") else int(nodeid_raw)
            else:
                nodeid = 0

            if len(ixx_raw) > 0:
                ixx = self.dataframe.parameter[ixx_raw[1:]].value if ixx_raw.startswith("&") else float(ixx_raw)
            else:
                ixx = 0.0

            if len(ixy_raw) > 0:
                ixy = self.dataframe.parameter[ixy_raw[1:]].value if ixy_raw.startswith("&") else float(ixy_raw)
            else:
                ixy = 0.0

            if len(ixz_raw) > 0:
                ixz = self.dataframe.parameter[ixz_raw[1:]].value if ixz_raw.startswith("&") else float(ixz_raw)
            else:
                ixz = 0.0

            if len(iyy_raw) > 0:
                iyy = self.dataframe.parameter[iyy_raw[1:]].value if iyy_raw.startswith("&") else float(iyy_raw)
            else:
                iyy = 0.0

            if len(iyz_raw) > 0:
                iyz = self.dataframe.parameter[iyz_raw[1:]].value if iyz_raw.startswith("&") else float(iyz_raw)
            else:
                iyz = 0.0

            if len(izz_raw) > 0:
                izz = self.dataframe.parameter[izz_raw[1:]].value if izz_raw.startswith("&") else float(izz_raw)
            else:
                izz = 0.0

            if len(vtx_raw) > 0:
                vtx = self.dataframe.parameter[vtx_raw[1:]].value if vtx_raw.startswith("&") else float(vtx_raw)
            else:
                vtx = 0.0

            if len(vty_raw) > 0:
                vty = self.dataframe.parameter[vty_raw[1:]].value if vty_raw.startswith("&") else float(vty_raw)
            else:
                vty = 0.0

            if len(vtz_raw) > 0:
                vtz = self.dataframe.parameter[vtz_raw[1:]].value if vtz_raw.startswith("&") else float(vtz_raw)
            else:
                vtz = 0.0

            if len(vrx_raw) > 0:
                vrx = self.dataframe.parameter[vrx_raw[1:]].value if vrx_raw.startswith("&") else float(vrx_raw)
            else:
                vrx = 0.0

            if len(vry_raw) > 0:
                vry = self.dataframe.parameter[vry_raw[1:]].value if vry_raw.startswith("&") else float(vry_raw)
            else:
                vry = 0.0

            if len(vrz_raw) > 0:
                vrz = self.dataframe.parameter[vrz_raw[1:]].value if vrz_raw.startswith("&") else float(vrz_raw)
            else:
                vrz = 0.0

            self.dataframe.part[pid] = Part(name=name,
                                            pid=pid,
                                            secid=secid,
                                            mid=mid,
                                            eosid=eosid,
                                            hgid=hgid,
                                            grav=grav,
                                            adpopt=adpopt,
                                            tmid=tmid,
                                            xc=xc,
                                            yc=yc,
                                            zc=zc,
                                            tm=tm,
                                            ircs=ircs,
                                            nodeid=nodeid,
                                            ixx=ixx,
                                            ixy=ixy,
                                            ixz=ixz,
                                            iyy=iyy,
                                            iyz=iyz,
                                            izz=izz,
                                            vtx=vtx,
                                            vty=vty,
                                            vtz=vtz,
                                            vrx=vrx,
                                            vry=vry,
                                            vrz=vrz,
                                            )
            self.dataframe.part_tensor.append([pid, secid, mid, eosid, hgid])

            self.reset()

            return