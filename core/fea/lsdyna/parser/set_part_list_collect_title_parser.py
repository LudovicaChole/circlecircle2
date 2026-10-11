from core.fea.parser import Parser
from core.fea.model.lsdyna.set_part_list import SetPartList
from .card_fields import fields, number


class SetPartListCollectTitleParser(Parser):
    def __init__(self):
        super().__init__()
        self.version = {"12.0": self._read, "13.0": self._read, "16.0": self._read}

    def _read(self, line_raw):
        if self.line_number == 0:
            self.temp.append(line_raw.strip())
        elif self.line_number == 1:
            vals = fields(line_raw)
            self.current_id = number(vals[0], self.dataframe, integer=True)
            self.dataframe.set_part_list.setdefault(self.current_id, SetPartList(uid=self.current_id, name=self.temp[0], solver=vals[5] or 'MECH'))
        else:
            obj = self.dataframe.set_part_list[self.current_id]
            for raw in fields(line_raw):
                nid = number(raw, self.dataframe, integer=True)
                if nid and nid not in obj.ids:
                    obj.ids.append(nid)
        self.line_number += 1
