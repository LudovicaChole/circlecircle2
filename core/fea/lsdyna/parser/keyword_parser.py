from core.fea.parser import Parser
from core.fea.model.lsdyna.keyword import KeyWord


class KeyWordParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        uid = len(self.dataframe.keyword) + 1

        self.dataframe.keyword[uid] = KeyWord(uid=uid)

        self.reset()

