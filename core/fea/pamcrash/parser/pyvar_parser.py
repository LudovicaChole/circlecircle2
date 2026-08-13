from core.fea.parser import Parser
from core.fea.pamcrash.keywords.pyvar import Pyvar


class PyvarParser(Parser):
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
            raise Exception(f"pam-crash version {version} is not supported for PYVAR keyword\n {e}") from e

    def _2020(self, line_raw):
        if self.line_number == 0:
            pyvarid_raw = line_raw[8:16].strip()

            self.temp.append(pyvarid_raw)

            self.line_number = 1

            return

        if self.line_number == 1:
            name_raw = line_raw[5:].strip()

            self.temp.append(name_raw)

            self.line_number = 2

            return

        if self.line_number == 2:
            pyvarid_raw = self.temp[0]
            name_raw = self.temp[1]

            value_raw = line_raw.split("=")[1].strip()

            if len(pyvarid_raw) > 0:
                pyvarid = int(pyvarid_raw)
            else:
                pyvarid = 0

            if len(name_raw) > 0:
                name = name_raw
            else:
                name = "default_"

            if len(value_raw) > 0:
                value = value_raw
            else:
                value = 0

            uid = len(self.dataframe.parameter) + 1

            self.dataframe.parameter[name] = Pyvar(uid=uid,
                                                   pyvarid=pyvarid,
                                                   name=name,
                                                   value=value)

            self.reset()