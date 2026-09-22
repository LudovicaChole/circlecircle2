from core.fea.parser import Parser
from core.fea.lsdyna.keywords.set_part_list import SetPartList


class SetPartListGenerateParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

        self.current_set_list_id = None

    def _12p0(self, line_raw):
        if self.line_number == 0:
            sid = int(line_raw[0:10].strip())

            da1 = 0
            da2 = 0
            da3 = 0
            da4 = 0
            solver = "MECH"

            self.dataframe.set_part_list[sid] = SetPartList(uid=sid,
                                                            da1=da1,
                                                            da2=da2,
                                                            da3=da3,
                                                            da4=da4,
                                                            solver=solver)

            self.current_set_list_id = sid

            self.line_number = 1

            return

        if self.line_number != 0:
            line_list = line_raw.strip().split()

            begin = int(line_list[0])

            end = int(line_list[1])

            current_set_list_object = self.dataframe.set_part_list[self.current_set_list_id]

            for i in range(begin, end + 1):
                current_set_list_object.ids.append(i)

            # More range cards may follow under the same set keyword.

            return

