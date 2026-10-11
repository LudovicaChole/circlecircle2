from core.fea.lsdyna.parser.card_fields import fields, number
from core.fea.mesh_data import insert
from core.fea.parser import Parser
from core.fea.model.lsdyna.element_shell import ElementShell


class ElementShellParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        values = fields(line_raw, (8,)*10)
        uid_raw, pid_raw, n1_raw, n2_raw, n3_raw, n4_raw = values[:6]

        uid = number(uid_raw, self.dataframe, integer=True)
        pid = number(pid_raw, self.dataframe, integer=True)
        n1 = number(n1_raw, self.dataframe, integer=True)
        n2 = number(n2_raw, self.dataframe, integer=True)
        n3 = number(n3_raw, self.dataframe, integer=True)
        n4 = number(n4_raw, self.dataframe, integer=True)

        if any(number(value, self.dataframe, integer=True) for value in values[6:]):
            raise ValueError('Higher-order ELEMENT_SHELL nodes are not supported; conversion would discard midside nodes')
        n4 = n4 or n3
        if uid in self.dataframe.element_shell:
            raise ValueError(f'Duplicate shell identifier {uid}')
        self.dataframe.element_shell[uid] = ElementShell(uid=uid,
                                                         pid=pid,
                                                         n1=n1,
                                                         n2=n2,
                                                         n3=n3,
                                                         n4=n4)
        self.dataframe.element_shell_tensor.append([uid, pid, n1, n2, n3, n4])

        self.dataframe.storge_part_element.setdefault(pid, [])
        self.dataframe.storge_part_element[pid].append(self.dataframe.element_shell[uid])

        self.dataframe.storge_part_node_xyz.setdefault(pid, set())
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n1].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n2].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n3].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n4].xyz)

        self.dataframe.storge_part_node_id.setdefault(pid, set())
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n1].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n2].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n3].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n4].uid)

        self.reset()
