from core.fea.parser import Parser
from core.fea.model.lsdyna.contact_automatic_single_surface_id import ContactAutomaticSingleSurfaceID


class ContactAutomaticSingleSurfaceIDTitleParser(Parser):
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
            cid_raw = line_raw[0:10].strip()
            heading_raw = line_raw[10:80].strip()

            self.temp.append(cid_raw)
            self.temp.append(heading_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            ssid_raw = line_raw[0:10].strip()
            msid_raw = line_raw[10:20].strip()
            sstyp_raw = line_raw[20:30].strip()
            mstyp_raw = line_raw[30:40].strip()
            sboxid_raw = line_raw[40:50].strip()
            mboxid_raw = line_raw[50:60].strip()
            spr_raw = line_raw[60:70].strip()
            mpr_raw = line_raw[70:80].strip()

            self.temp.append(ssid_raw)
            self.temp.append(msid_raw)
            self.temp.append(sstyp_raw)
            self.temp.append(mstyp_raw)
            self.temp.append(sboxid_raw)
            self.temp.append(mboxid_raw)
            self.temp.append(spr_raw)
            self.temp.append(mpr_raw)

            self.line_number = 3

            return

        if self.line_number == 3:
            fs_raw = line_raw[0:10].strip()
            fd_raw = line_raw[10:20].strip()
            dc_raw = line_raw[20:30].strip()
            vc_raw = line_raw[30:40].strip()
            vdc_raw = line_raw[40:50].strip()
            penchk_raw = line_raw[50:60].strip()
            bt_raw = line_raw[60:70].strip()
            dt_raw = line_raw[70:80].strip()

            self.temp.append(fs_raw)
            self.temp.append(fd_raw)
            self.temp.append(dc_raw)
            self.temp.append(vc_raw)
            self.temp.append(vdc_raw)
            self.temp.append(penchk_raw)
            self.temp.append(bt_raw)
            self.temp.append(dt_raw)

            self.line_number = 4

            return

        if self.line_number == 4:
            name_raw = self.temp[0]
            cid_raw = self.temp[1]
            heading_raw = self.temp[2]
            ssid_raw = self.temp[3]
            msid_raw = self.temp[4]
            sstyp_raw = self.temp[5]
            mstyp_raw = self.temp[6]
            sboxid_raw = self.temp[7]
            mboxid_raw = self.temp[8]
            spr_raw = self.temp[9]
            mpr_raw = self.temp[10]
            fs_raw = self.temp[11]
            fd_raw = self.temp[12]
            dc_raw = self.temp[13]
            vc_raw = self.temp[14]
            vdc_raw = self.temp[15]
            penchk_raw = self.temp[16]
            bt_raw = self.temp[17]
            dt_raw = self.temp[18]

            sfs_raw = line_raw[0:10].strip()
            sfm_raw = line_raw[10:20].strip()
            sst_raw = line_raw[20:30].strip()
            mst_raw = line_raw[30:40].strip()
            sfst_raw = line_raw[40:50].strip()
            sfmt_raw = line_raw[50:60].strip()
            fsf_raw = line_raw[60:70].strip()
            vsf_raw = line_raw[70:80].strip()

            name = name_raw
            cid = cid_raw[1:] if cid_raw.startswith("&") else int(cid_raw)
            heading = heading_raw[1:] if heading_raw.startswith("&") else heading_raw

            if len(ssid_raw) > 0:
                ssid = ssid_raw[1:] if ssid_raw.startswith("&") else int(ssid_raw)
            else:
                ssid = 0

            if len(msid_raw) > 0:
                msid = msid_raw[1:] if msid_raw.startswith("&") else int(msid_raw)
            else:
                msid = 0

            if len(sstyp_raw) > 0:
                sstyp = sstyp_raw[1:] if sstyp_raw.startswith("&") else int(sstyp_raw)
            else:
                sstyp = 0

            if len(mstyp_raw) > 0:
                mstyp = mstyp_raw[1:] if mstyp_raw.startswith("&") else int(mstyp_raw)
            else:
                mstyp = 0

            if len(sboxid_raw) > 0:
                sboxid = sboxid_raw[1:] if sboxid_raw.startswith("&") else int(sboxid_raw)
            else:
                sboxid = 0.0

            if len(mboxid_raw) > 0:
                mboxid = mboxid_raw[1:] if mboxid_raw.startswith("&") else int(mboxid_raw)
            else:
                mboxid = 0.0

            if len(spr_raw) > 0:
                spr = spr_raw[1:] if spr_raw.startswith("&") else float(spr_raw)
            else:
                spr = 0.0

            if len(mpr_raw) > 0:
                mpr = mpr_raw[1:] if mpr_raw.startswith("&") else float(mpr_raw)
            else:
                mpr = 0.0

            if len(fs_raw) > 0:
                fs = fs_raw[1:] if fs_raw.startswith("&") else float(fs_raw)
            else:
                fs = 0.0

            if len(fd_raw) > 0:
                fd = fd_raw[1:] if fd_raw.startswith("&") else float(fd_raw)
            else:
                fd = 0.0

            if len(dc_raw) > 0:
                dc = dc_raw[1:] if dc_raw.startswith("&") else float(dc_raw)
            else:
                dc = 0.0

            if len(vc_raw) > 0:
                vc = vc_raw[1:] if vc_raw.startswith("&") else float(vc_raw)
            else:
                vc = 0.0

            if len(vdc_raw) > 0:
                vdc = vdc_raw[1:] if vdc_raw.startswith("&") else float(vdc_raw)
            else:
                vdc = 0.0

            if len(penchk_raw) > 0:
                penchk = penchk_raw[1:] if penchk_raw.startswith("&") else float(penchk_raw)
            else:
                penchk = 0.0

            if len(bt_raw) > 0:
                bt = bt_raw[1:] if bt_raw.startswith("&") else float(bt_raw)
            else:
                bt = 0.0

            if len(dt_raw) > 0:
                dt = dt_raw[1:] if dt_raw.startswith("&") else float(dt_raw)
            else:
                dt = 0.0

            if len(sfs_raw) > 0:
                sfs = sfs_raw[1:] if sfs_raw.startswith("&") else float(sfs_raw)
            else:
                sfs = 0.0

            if len(sfm_raw) > 0:
                sfm = sfm_raw[1:] if sfm_raw.startswith("&") else float(sfm_raw)
            else:
                sfm = 0.0

            if len(sst_raw) > 0:
                sst = sst_raw[1:] if sst_raw.startswith("&") else float(sst_raw)
            else:
                sst = 0.0

            if len(mst_raw) > 0:
                mst = mst_raw[1:] if mst_raw.startswith("&") else float(mst_raw)
            else:
                mst = 0.0

            if len(sfst_raw) > 0:
                sfst = sfst_raw[1:] if sfst_raw.startswith("&") else float(sfst_raw)
            else:
                sfst = 0.0

            if len(sfmt_raw) > 0:
                sfmt = sfmt_raw[1:] if sfmt_raw.startswith("&") else float(sfmt_raw)
            else:
                sfmt = 0.0

            if len(fsf_raw) > 0:
                fsf = fsf_raw[1:] if fsf_raw.startswith("&") else float(fsf_raw)
            else:
                fsf = 0.0

            if len(vsf_raw) > 0:
                vsf = vsf_raw[1:] if vsf_raw.startswith("&") else float(vsf_raw)
            else:
                vsf = 0.0

            self.dataframe.contact_automatic_single_surface_id[cid] = ContactAutomaticSingleSurfaceID(
                uid=cid,
                heading=heading,
                ssid=ssid,
                msid=msid,
                sstyp=sstyp,
                mstyp=mstyp,
                sboxid=sboxid,
                mboxid=mboxid,
                spr=spr,
                mpr=mpr,
                fs=fs,
                fd=fd,
                dc=dc,
                vc=vc,
                vdc=vdc,
                penchk=penchk,
                bt=bt,
                dt=dt,
                sfs=sfs,
                sfm=sfm,
                sst=sst,
                mst=mst,
                sfst=sfst,
                sfmt=sfmt,
                fsf=fsf,
                vsf=vsf,
                name=name
            )

            ss = self.check_contact_type(c_id=ssid, c_type=sstyp)
            ms = self.check_contact_type(c_id=msid, c_type=mstyp)

            self.dataframe.contact_automatic_single_surface_id[cid].ss = ss
            self.dataframe.contact_automatic_single_surface_id[cid].ms = ms

            self.reset()

            return

    def check_contact_type(self, c_id, c_type):
        if c_type == 0:
            return None

        elif c_type == 1:
            return None

        elif c_type == 2:
            if c_id in self.dataframe.set_part_list:
                return self.dataframe.set_part_list[c_id]
            else:
                return None

        elif c_type == 3:
            if c_id in self.dataframe.part:
                return self.dataframe.part[c_id]
            else:
                return None