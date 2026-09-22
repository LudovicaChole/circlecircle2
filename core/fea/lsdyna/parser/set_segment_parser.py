from core.fea.parser import Parser
from core.fea.lsdyna.keywords.set_segment import SetSegment


class SetSegmentParser(Parser):
    def __init__(self, title=False):
        super().__init__()
        self.title = title
        self.version = {"12.0": self._12p0, "13.0": self._12p0}

    def _value(self, raw):
        raw = raw.strip()
        return int(self.dataframe.parameter[raw[1:]].value) if raw.startswith("&") else int(raw or 0)

    def _12p0(self, line_raw):
        if self.title and self.line_number == 0:
            self.temp.append(line_raw.strip())
            self.line_number += 1
            return
        fields = line_raw.rstrip("\r\n").split(",") if "," in line_raw else [line_raw[i:i + 10] for i in range(0, 80, 10)]
        if self.line_number == int(self.title):
            uid = self._value(fields[0])
            self.current_set = SetSegment(uid, self.temp[0] if self.title else "default")
            self.dataframe.set_segment[uid] = self.current_set
            self.line_number += 1
            return
        nodes = [self._value(raw) for raw in fields[:4]]
        if not any(nodes):
            return
        nodes = tuple(dict.fromkeys(node for node in nodes if node))
        if len(nodes) not in (3, 4):
            raise ValueError(f"Invalid segment in set {self.current_set.uid}: {nodes}")
        self.current_set.segments.append(nodes)
