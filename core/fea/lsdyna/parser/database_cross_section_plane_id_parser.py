from core.fea.parser import Parser
from core.fea.model.lsdyna.database_cross_section_plane_id import DatabaseCrossSectionPlaneID


class DatabaseCrossSectionPlaneIDParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            csid_raw = line_raw[0:10].strip()
            name_raw = line_raw[10:80].strip()

            self.temp.append(csid_raw)
            self.temp.append(name_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            psid_raw = line_raw[0:10].strip()
            xct_raw = line_raw[10:20].strip()
            yct_raw = line_raw[20:30].strip()
            zct_raw = line_raw[30:40].strip()
            xch_raw = line_raw[40:50].strip()
            ych_raw = line_raw[50:60].strip()
            zch_raw = line_raw[60:70].strip()
            radius_raw = line_raw[70:80].strip()

            self.temp.append(psid_raw)
            self.temp.append(xct_raw)
            self.temp.append(yct_raw)
            self.temp.append(zct_raw)
            self.temp.append(xch_raw)
            self.temp.append(ych_raw)
            self.temp.append(zch_raw)
            self.temp.append(radius_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            csid_raw = self.temp[0]
            name_raw = self.temp[1]
            psid_raw = self.temp[2]
            xct_raw = self.temp[3]
            yct_raw = self.temp[4]
            zct_raw = self.temp[5]
            xch_raw = self.temp[6]
            ych_raw = self.temp[7]
            zch_raw = self.temp[8]
            radius_raw = self.temp[9]

            xhev_raw = line_raw[0:10].strip()
            yhev_raw = line_raw[10:20].strip()
            zhev_raw = line_raw[20:30].strip()
            lenl_raw = line_raw[30:40].strip()
            lenm_raw = line_raw[40:50].strip()
            did_raw = line_raw[50:60].strip()
            itype_raw = line_raw[60:70].strip()

            csid = csid_raw[1:] if csid_raw.startswith("&") else int(csid_raw)
            name = name_raw[1:] if name_raw.startswith("&") else name_raw

            if len(psid_raw) > 0:
                psid = psid_raw[1:] if psid_raw.startswith("&") else int(psid_raw)
            else:
                psid = 0

            if len(xct_raw) > 0:
                xct = xct_raw[1:] if xct_raw.startswith("&") else float(xct_raw)
            else:
                xct = 0.0

            if len(yct_raw) > 0:
                yct = yct_raw[1:] if yct_raw.startswith("&") else float(yct_raw)
            else:
                yct = 0.0

            if len(zct_raw) > 0:
                zct = zct_raw[1:] if zct_raw.startswith("&") else float(zct_raw)
            else:
                zct = 0.0

            if len(xch_raw) > 0:
                xch = xch_raw[1:] if xch_raw.startswith("&") else float(xch_raw)
            else:
                xch = 0.0

            if len(ych_raw) > 0:
                ych = ych_raw[1:] if ych_raw.startswith("&") else float(ych_raw)
            else:
                ych = 0.0

            if len(zch_raw) > 0:
                zch = zch_raw[1:] if zch_raw.startswith("&") else float(zch_raw)
            else:
                zch = 0.0

            if len(radius_raw) > 0:
                radius = radius_raw[1:] if radius_raw.startswith("&") else float(radius_raw)
            else:
                radius = 0.0

            if len(xhev_raw) > 0:
                xhev = xhev_raw[1:] if xhev_raw.startswith("&") else float(xhev_raw)
            else:
                xhev = 0.0

            if len(yhev_raw) > 0:
                yhev = yhev_raw[1:] if yhev_raw.startswith("&") else float(yhev_raw)
            else:
                yhev = 0.0

            if len(zhev_raw) > 0:
                zhev = zhev_raw[1:] if zhev_raw.startswith("&") else float(zhev_raw)
            else:
                zhev = 0.0

            if len(lenl_raw) > 0:
                lenl = lenl_raw[1:] if lenl_raw.startswith("&") else float(lenl_raw)
            else:
                lenl = 0.0

            if len(lenm_raw) > 0:
                lenm = lenm_raw[1:] if lenm_raw.startswith("&") else float(lenm_raw)
            else:
                lenm = 0.0

            if len(did_raw) > 0:
                did = did_raw[1:] if did_raw.startswith("&") else int(did_raw)
            else:
                did = 0

            if len(itype_raw) > 0:
                itype = itype_raw[1:] if itype_raw.startswith("&") else int(itype_raw)
            else:
                itype = 0

            self.dataframe.database_cross_section_plane_id[csid] = DatabaseCrossSectionPlaneID(uid=csid,
                                                                                               name=name,
                                                                                               psid=psid,
                                                                                               xct=xct,
                                                                                               yct=yct,
                                                                                               zct=zct,
                                                                                               xch=xch,
                                                                                               ych=ych,
                                                                                               zch=zch,
                                                                                               radius=radius,
                                                                                               xhev=xhev,
                                                                                               yhev=yhev,
                                                                                               zhev=zhev,
                                                                                               lenl=lenl,
                                                                                               lenm=lenm,
                                                                                               did=did,
                                                                                               itype=itype)

            if psid in self.dataframe.set_part_list:
                self.dataframe.database_cross_section_plane_id[csid].pset = self.dataframe.set_part_list[psid]

            self.reset()

            return
