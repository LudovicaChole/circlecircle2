from core.fea.parser import Parser
from core.fea.model.lsdyna.contact_automatic_surface_to_surface_id import ContactAutomaticSurfaceToSurfaceID


class ContactAutomaticSurfaceToSurfaceIDTitleParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number >= 5:
            return    # Ignore optional cards until the next keyword resets this parser.

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
            cid = self.dataframe.parameter[cid_raw[1:]].value if cid_raw.startswith("&") else int(cid_raw)
            heading = self.dataframe.parameter[heading_raw[1:]].value if heading_raw.startswith("&") else heading_raw

            if len(ssid_raw) > 0:
                ssid = self.dataframe.parameter[ssid_raw[1:]].value if ssid_raw.startswith("&") else int(ssid_raw)
            else:
                ssid = 0

            if len(msid_raw) > 0:
                msid = self.dataframe.parameter[msid_raw[1:]].value if msid_raw.startswith("&") else int(msid_raw)
            else:
                msid = 0

            if len(sstyp_raw) > 0:
                sstyp = self.dataframe.parameter[sstyp_raw[1:]].value if sstyp_raw.startswith("&") else int(sstyp_raw)
            else:
                sstyp = 0

            if len(mstyp_raw) > 0:
                mstyp = self.dataframe.parameter[mstyp_raw[1:]].value if mstyp_raw.startswith("&") else int(mstyp_raw)
            else:
                mstyp = 0

            if len(sboxid_raw) > 0:
                sboxid = self.dataframe.parameter[sboxid_raw[1:]].value if sboxid_raw.startswith("&") else int(sboxid_raw)
            else:
                sboxid = 0.0

            if len(mboxid_raw) > 0:
                mboxid = self.dataframe.parameter[mboxid_raw[1:]].value if mboxid_raw.startswith("&") else int(mboxid_raw)
            else:
                mboxid = 0.0

            if len(spr_raw) > 0:
                spr = self.dataframe.parameter[spr_raw[1:]].value if spr_raw.startswith("&") else float(spr_raw)
            else:
                spr = 0.0

            if len(mpr_raw) > 0:
                mpr = self.dataframe.parameter[mpr_raw[1:]].value if mpr_raw.startswith("&") else float(mpr_raw)
            else:
                mpr = 0.0

            if len(fs_raw) > 0:
                fs = self.dataframe.parameter[fs_raw[1:]].value if fs_raw.startswith("&") else float(fs_raw)
            else:
                fs = 0.0

            if len(fd_raw) > 0:
                fd = self.dataframe.parameter[fd_raw[1:]].value if fd_raw.startswith("&") else float(fd_raw)
            else:
                fd = 0.0

            if len(dc_raw) > 0:
                dc = self.dataframe.parameter[dc_raw[1:]].value if dc_raw.startswith("&") else float(dc_raw)
            else:
                dc = 0.0

            if len(vc_raw) > 0:
                vc = self.dataframe.parameter[vc_raw[1:]].value if vc_raw.startswith("&") else float(vc_raw)
            else:
                vc = 0.0

            if len(vdc_raw) > 0:
                vdc = self.dataframe.parameter[vdc_raw[1:]].value if vdc_raw.startswith("&") else float(vdc_raw)
            else:
                vdc = 0.0

            if len(penchk_raw) > 0:
                penchk = self.dataframe.parameter[penchk_raw[1:]].value if penchk_raw.startswith("&") else float(penchk_raw)
            else:
                penchk = 0.0

            if len(bt_raw) > 0:
                bt = self.dataframe.parameter[bt_raw[1:]].value if bt_raw.startswith("&") else float(bt_raw)
            else:
                bt = 0.0

            if len(dt_raw) > 0:
                dt = self.dataframe.parameter[dt_raw[1:]].value if dt_raw.startswith("&") else float(dt_raw)
            else:
                dt = 0.0

            if len(sfs_raw) > 0:
                sfs = self.dataframe.parameter[sfs_raw[1:]].value if sfs_raw.startswith("&") else float(sfs_raw)
            else:
                sfs = 0.0

            if len(sfm_raw) > 0:
                sfm = self.dataframe.parameter[sfm_raw[1:]].value if sfm_raw.startswith("&") else float(sfm_raw)
            else:
                sfm = 0.0

            if len(sst_raw) > 0:
                sst = self.dataframe.parameter[sst_raw[1:]].value if sst_raw.startswith("&") else float(sst_raw)
            else:
                sst = 0.0

            if len(mst_raw) > 0:
                mst = self.dataframe.parameter[mst_raw[1:]].value if mst_raw.startswith("&") else float(mst_raw)
            else:
                mst = 0.0

            if len(sfst_raw) > 0:
                sfst = self.dataframe.parameter[sfst_raw[1:]].value if sfst_raw.startswith("&") else float(sfst_raw)
            else:
                sfst = 0.0

            if len(sfmt_raw) > 0:
                sfmt = self.dataframe.parameter[sfmt_raw[1:]].value if sfmt_raw.startswith("&") else float(sfmt_raw)
            else:
                sfmt = 0.0

            if len(fsf_raw) > 0:
                fsf = self.dataframe.parameter[fsf_raw[1:]].value if fsf_raw.startswith("&") else float(fsf_raw)
            else:
                fsf = 0.0

            if len(vsf_raw) > 0:
                vsf = self.dataframe.parameter[vsf_raw[1:]].value if vsf_raw.startswith("&") else float(vsf_raw)
            else:
                vsf = 0.0

            self.dataframe.contact_automatic_surface_to_surface_id[cid] = ContactAutomaticSurfaceToSurfaceID(
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

            self.dataframe.contact_automatic_surface_to_surface_id[cid].ss = ss
            self.dataframe.contact_automatic_surface_to_surface_id[cid].ms = ms

            self.line_number = 5

            return

    def check_contact_type(self, c_id, c_type):
        if c_type == 0:
            return self.dataframe.set_segment.get(c_id)

        elif c_type == 1:
            return self.dataframe.set_shell_list.get(c_id)

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