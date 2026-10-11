from core.fea.parser import Parser
from core.fea.model.lsdyna.element_solid import ElementSolid
from core.fea.lsdyna.parser.card_fields import fields, number


class ElementSolidParser(Parser):
    def __init__(self):
        super().__init__()

        self.version = {
            "12.0": self._12p0,
            "13.0": self._12p0, "16.0": self._12p0,
        }

    def _12p0(self, line_raw):
        values = fields(line_raw, (8,)*10)
        if self.line_number == 0:
            self.temp = values[:2]
            self.line_number = 1
            if not any(values[2:]):
                return
            nodes = values[2:10]
        else:
            nodes = fields(line_raw, (8,)*8)
        if any(not raw for raw in [*self.temp, *nodes]):
            raise ValueError('ELEMENT_SOLID: missing EID, PID or connectivity field')
        uid, pid = [number(raw, self.dataframe, integer=True) for raw in self.temp]
        n1,n2,n3,n4,n5,n6,n7,n8 = [number(raw,self.dataframe,integer=True) for raw in nodes]
        if min(uid,pid,n1,n2,n3,n4,n5,n6,n7,n8) <= 0:
            raise ValueError('ELEMENT_SOLID: identifiers must be positive')
        self.dataframe.element_solid[uid] = ElementSolid(uid=uid,
                                                         pid=pid,
                                                         n1=n1,
                                                         n2=n2,
                                                         n3=n3,
                                                         n4=n4,
                                                         n5=n5,
                                                         n6=n6,
                                                         n7=n7,
                                                         n8=n8)
        self.dataframe.element_solid_tensor.append([uid, pid, n1, n2, n3, n4, n5, n6, n7, n8])

        solid_surface_tensor = self.dataframe.element_solid[uid].surface_tensor
        self.dataframe.element_solid_surface_tensor.extend(solid_surface_tensor)

        self.dataframe.storge_part_element.setdefault(pid, [])
        self.dataframe.storge_part_element[pid].append(self.dataframe.element_solid[uid])

        self.dataframe.storge_part_node_xyz.setdefault(pid, set())
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n1].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n2].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n3].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n4].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n5].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n6].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n7].xyz)
        self.dataframe.storge_part_node_xyz[pid].add(self.dataframe.node[n8].xyz)

        self.dataframe.storge_part_node_id.setdefault(pid, set())
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n1].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n2].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n3].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n4].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n5].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n6].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n7].uid)
        self.dataframe.storge_part_node_id[pid].add(self.dataframe.node[n8].uid)

        self.reset()

        return
