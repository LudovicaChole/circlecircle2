from core.fea.parser import Parser
from core.fea.lsdyna.parser.history_node_fields import history_node_fields
from core.fea.lsdyna.keywords.database_history_node import DatabaseHistoryNode


class DatabaseHistoryNodeTitleParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0,
        }

        self.current_name = None

    def _12p0(self, line_raw):
        if self.line_number == 0:
            name = line_raw.strip()

            self.dataframe.database_history_node.setdefault(name, DatabaseHistoryNode(uid=1, name=name))

            self.current_name = name

            self.line_number = 1

            return

        if self.line_number == 1:

            data_list = history_node_fields(line_raw)

            current_object = self.dataframe.database_history_node[self.current_name]

            current_object.ids.extend(data_list)

            self.line_number = 2

            return

        if self.line_number != 0 and self.line_number != 1:
            data_list = history_node_fields(line_raw)

            current_object = self.dataframe.database_history_node[self.current_name]

            current_object.ids.extend(data_list)

            return
