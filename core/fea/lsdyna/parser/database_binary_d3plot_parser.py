from core.fea.parser import Parser
from core.fea.lsdyna.keywords.database_binary_d3plot import DatabaseBinaryD3plot


class DatabaseBinaryD3plotParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

    def _12p0(self, line_raw):
        if self.line_number == 0:
            dt_raw = line_raw[0:10].strip()
            lcdt_raw = line_raw[10:20].strip()
            beam_raw = line_raw[20:30].strip()
            npltc_raw = line_raw[30:40].strip()
            psepid_raw = line_raw[40:50].strip()

            self.temp.append(dt_raw)
            self.temp.append(lcdt_raw)
            self.temp.append(beam_raw)
            self.temp.append(npltc_raw)
            self.temp.append(psepid_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            dt_raw = self.temp[0]
            lcdt_raw = self.temp[1]
            beam_raw = self.temp[2]
            npltc_raw = self.temp[3]
            psepid_raw = self.temp[4]

            ioopt_raw = line_raw[0:10].strip()
            rate_raw = line_raw[10:20].strip()
            cutoff_raw = line_raw[20:30].strip()
            window_raw = line_raw[30:40].strip()
            ptype_raw = line_raw[40:50].strip()
            pset_raw = line_raw[50:60].strip()

            if len(dt_raw) > 0:
                dt = self.dataframe.parameter[dt_raw[1:]].value if dt_raw.startswith("&") else float(dt_raw)
            else:
                dt = 0

            if len(lcdt_raw) > 0:
                lcdt = self.dataframe.parameter[lcdt_raw[1:]].value if lcdt_raw.startswith("&") else int(lcdt_raw)
            else:
                lcdt = 0

            if len(beam_raw) > 0:
                beam = self.dataframe.parameter[beam_raw[1:]].value if beam_raw.startswith("&") else float(beam_raw)
            else:
                beam = 0

            if len(npltc_raw) > 0:
                npltc = self.dataframe.parameter[npltc_raw[1:]].value if npltc_raw.startswith("&") else float(npltc_raw)
            else:
                npltc = 0

            if len(psepid_raw) > 0:
                psepid = self.dataframe.parameter[psepid_raw[1:]].value if psepid_raw.startswith("&") else float(psepid_raw)
            else:
                psepid = 0

            if len(ioopt_raw) > 0:
                ioopt = self.dataframe.parameter[ioopt_raw[1:]].value if ioopt_raw.startswith("&") else float(ioopt_raw)
            else:
                ioopt = 0

            if len(rate_raw) > 0:
                rate = self.dataframe.parameter[rate_raw[1:]].value if rate_raw.startswith("&") else float(rate_raw)
            else:
                rate = 0

            if len(cutoff_raw) > 0:
                cutoff = self.dataframe.parameter[cutoff_raw[1:]].value if cutoff_raw.startswith("&") else float(cutoff_raw)
            else:
                cutoff = 0

            if len(window_raw) > 0:
                window = self.dataframe.parameter[window_raw[1:]].value if window_raw.startswith("&") else float(window_raw)
            else:
                window = 0

            if len(ptype_raw) > 0:
                ptype = self.dataframe.parameter[ptype_raw[1:]].value if ptype_raw.startswith("&") else float(ptype_raw)
            else:
                ptype = 0

            if len(pset_raw) > 0:
                pset = self.dataframe.parameter[pset_raw[1:]].value if pset_raw.startswith("&") else float(pset_raw)
            else:
                pset = 0

            uid = len(self.dataframe.database_binary_d3plot) + 1

            self.dataframe.database_binary_d3plot[uid] = DatabaseBinaryD3plot(uid=uid,
                                                                              dt=dt,
                                                                              lcdt=lcdt,
                                                                              beam=beam,
                                                                              npltc=npltc,
                                                                              psepid=psepid,
                                                                              ioopt=ioopt,
                                                                              rate=rate,
                                                                              cutoff=cutoff,
                                                                              window=window,
                                                                              ptype=ptype,
                                                                              pset=pset,)

            self.reset()

            return
