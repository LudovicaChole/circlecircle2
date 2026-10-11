from types import SimpleNamespace
from core.fea.parser import Parser


class GroupParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {'2020': self._2020}

    def _2020(self, line_raw):
        self.temp.append(line_raw.rstrip())

    def finish(self):
        if not self.temp:
            return
        name = self.temp[0][8:].strip().strip("'\"")
        if not name or name in self.dataframe.storge['pam_groups']:
            raise ValueError(f'GROUP: missing or duplicate name {name}')
        self.dataframe.storge['pam_groups'][name] = SimpleNamespace(name=name, rows=self.temp[1:])
        self.reset()
