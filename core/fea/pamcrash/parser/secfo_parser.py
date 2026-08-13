from core.fea.parser import Parser
from core.fea.pamcrash.keywords.secfo import SecFo


class SecFoParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "2020": self._2020,
        }

    def parse(self, line_raw, version):
        """
        :param line_raw: raw data
        :return: Node Object
        """
        try:
            if version in self.version:
                self.version[version](line_raw)

        except Exception as e:
            raise Exception(f"pam-crash version {version} is not supported for SecFo keyword\n {e}") from e

    def _2020(self, line_raw):
        if self.line_number == 0:
            idsf_raw = line_raw[8:16].strip()
            ntyp_raw = line_raw[16:24].strip()
            ifra_raw = line_raw[24:32].strip()

            self.temp.append(idsf_raw)
            self.temp.append(ntyp_raw)
            self.temp.append(ifra_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            idsf_raw = self.temp[0]
            ntyp_raw = self.temp[1]
            ifra_raw = self.temp[2]

            name_raw = line_raw[8:].strip()

            if len(idsf_raw) > 0:
                idsf = self.dataframe.parameter[idsf_raw[1:]] if idsf_raw.startswith("&") else int(idsf_raw)
            else:
                idsf = 0

            if len(ntyp_raw) > 0:
                ntyp = self.dataframe.parameter[ntyp_raw[1:]] if ntyp_raw.startswith("&") else ntyp_raw
            else:
                ntyp = "SECTION"

            if len(ifra_raw) > 0:
                ifra = self.dataframe.parameter[ifra_raw[1:]] if ifra_raw.startswith("&") else float(ifra_raw)
            else:
                ifra = 0

            name = name_raw

            uid = len(self.dataframe.database_secforc) + 1

            self.dataframe.database_secforc[uid] = SecFo(uid=uid,
                                                         idsf=idsf,
                                                         ntyp=ntyp,
                                                         ifra=ifra,
                                                         name=name,
                                                         )

            self.current_entity_id = uid

            self.line_number = 2

            return

        if self.line_number == 2:
            entity_type = line_raw[0:11].strip().lower()

            if entity_type == "nod":
                nid_list = line_raw[11:].strip().split()

                self.dataframe.database_secforc[self.current_entity_id].entity_selection["nod"].update(nid_list)
            elif entity_type == "ele":
                ele_list = line_raw[11:].strip().split()

                self.dataframe.database_secforc[self.current_entity_id].entity_selection["ele"].update(ele_list)