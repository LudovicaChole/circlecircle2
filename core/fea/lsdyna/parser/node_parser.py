from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.mesh_data import insert
from core.fea.validation import required_id
from core.fea.parser import Parser
from core.fea.model.lsdyna.node import Node


class NodeParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        uid_raw, x_raw, y_raw, z_raw = fields(line_raw, (8,16,16,16,8,8))[:4]

        uid = number(uid_raw, self.dataframe, integer=True)
        x = number(x_raw, self.dataframe, integer=False)
        y = number(y_raw, self.dataframe, integer=False)
        z = number(z_raw, self.dataframe, integer=False)

        insert(self.dataframe.node, Node(uid=uid, x=x, y=y, z=z))
        self.dataframe.node_tensor.append([uid, x, y, z])
        self.dataframe.storge_node_id.append(uid)

        self.reset()

