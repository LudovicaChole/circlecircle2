from core.fea.parser import Parser
from core.fea.pamcrash.keywords.tetr4 import Tetr4


class Tetr4Parser(Parser):
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
            raise Exception(f"pam-crash version {version} is not supported for SHELL keyword\n {e}") from e

    def _2020(self, line_raw):
        idel_raw = line_raw[8:16].strip()
        idprt_raw = line_raw[16:24].strip()
        idnod1_raw = line_raw[24:32].strip()
        idnod2_raw = line_raw[32:40].strip()
        idnod3_raw = line_raw[40:48].strip()
        idnod4_raw = line_raw[48:56].strip()

        if len(idel_raw) > 0:
            idel = self.dataframe.parameter[idel_raw[1:]] if idel_raw.startswith("&") else int(idel_raw)
        else:
            idel = 0

        if len(idprt_raw) > 0:
            idprt = self.dataframe.parameter[idprt_raw[1:]] if idprt_raw.startswith("&") else int(idprt_raw)
        else:
            idprt = 0

        if len(idnod1_raw) > 0:
            idnod1 = self.dataframe.parameter[idnod1_raw[1:]] if idnod1_raw.startswith("&") else int(idnod1_raw)
        else:
            idnod1 = 0

        if len(idnod2_raw) > 0:
            idnod2 = self.dataframe.parameter[idnod2_raw[1:]] if idnod2_raw.startswith("&") else int(idnod2_raw)
        else:
            idnod2 = 0

        if len(idnod3_raw) > 0:
            idnod3 = self.dataframe.parameter[idnod3_raw[1:]] if idnod3_raw.startswith("&") else int(idnod3_raw)
        else:
            idnod3 = 0

        if len(idnod4_raw) > 0:
            idnod4 = self.dataframe.parameter[idnod4_raw[1:]] if idnod4_raw.startswith("&") else int(idnod4_raw)
        else:
            idnod4 = 0

        uid = len(self.dataframe.element_solid) + 1

        self.dataframe.element_solid[uid] = Tetr4(uid=uid,
                                                  idel=idel,
                                                  idprt=idprt,
                                                  idnod1=idnod1,
                                                  idnod2=idnod2,
                                                  idnod3=idnod3,
                                                  idnod4=idnod4,
                                                  tag="tetr4")

        self.reset()

