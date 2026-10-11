from core.fea.parser import Parser
from core.fea.model.lsdyna.end import End


class EndParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        uid = len(self.dataframe.end) + 1

        self.dataframe.end[uid] = End(uid=uid)

        self.reset()

