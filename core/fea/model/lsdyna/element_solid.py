from abc import ABC, abstractmethod
from core.fea.model.lsdyna.element_shell import ElementShell


class ElementSolid(ABC):
    """
    user defined element solid class
    input 4 parameters: uid, pid, node_id_1, node_id_2, node_id_3, node_id_4, node_id_5, node_id_6, node_id_7, node_id_8
    """
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.pid = kwargs.get("pid", args[1] if len(args) > 1 else None)
        self.n1 = kwargs.get("n1", args[2] if len(args) > 2 else None)
        self.n2 = kwargs.get("n2", args[3] if len(args) > 3 else None)
        self.n3 = kwargs.get("n3", args[4] if len(args) > 4 else None)
        self.n4 = kwargs.get("n4", args[5] if len(args) > 5 else None)
        self.n5 = kwargs.get("n5", args[6] if len(args) > 6 else None)
        self.n6 = kwargs.get("n6", args[7] if len(args) > 7 else None)
        self.n7 = kwargs.get("n7", args[8] if len(args) > 8 else None)
        self.n8 = kwargs.get("n8", args[9] if len(args) > 9 else None)

        self.format = None

        self.surface = {}
        self.surface_tensor = []

        self._check_element_info()

    def _check_element_info(self):
        if self.n4 == self.n5 and self.n4 == self.n6 and self.n4 == self.n7 and self.n4 == self.n8:
            self.surface[-1] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n3, n4=self.n3)
            self.surface[-2] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n4, n4=self.n4)
            self.surface[-3] = ElementShell(uid=-1, pid=self.pid, n1=self.n2, n2=self.n3, n3=self.n4, n4=self.n4)
            self.surface[-4] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n3, n3=self.n4, n4=self.n4)

            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n3, self.n3])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n4, self.n4])
            self.surface_tensor.append([-1, self.pid, self.n2, self.n3, self.n4, self.n4])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n3, self.n4, self.n4])

            self.format = "tetra4"

        elif self.n4 != self.n5 and self.n5 == self.n6 and self.n5 == self.n7 and self.n5 == self.n8:
            self.surface[-1] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n3, n4=self.n4)
            self.surface[-2] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n5, n3=self.n4, n4=self.n4)
            self.surface[-3] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n5, n4=self.n5)
            self.surface[-4] = ElementShell(uid=-1, pid=self.pid, n1=self.n2, n2=self.n3, n3=self.n5, n4=self.n5)
            self.surface[-5] = ElementShell(uid=-1, pid=self.pid, n1=self.n3, n2=self.n4, n3=self.n5, n4=self.n5)

            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n3, self.n4])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n5, self.n4, self.n4])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n5, self.n5])
            self.surface_tensor.append([-1, self.pid, self.n2, self.n3, self.n5, self.n5])
            self.surface_tensor.append([-1, self.pid, self.n3, self.n4, self.n5, self.n5])

            self.format = "pyramid5"

        elif self.n4 != self.n5 and self.n5 == self.n6 and self.n6 != self.n7 and self.n7 == self.n8:
            self.surface[-1] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n3, n4=self.n4)
            self.surface[-2] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n4, n3=self.n7, n4=self.n5)
            self.surface[-3] = ElementShell(uid=-1, pid=self.pid, n1=self.n2, n2=self.n3, n3=self.n7, n4=self.n5)
            self.surface[-4] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n5, n4=self.n5)
            self.surface[-5] = ElementShell(uid=-1, pid=self.pid, n1=self.n4, n2=self.n3, n3=self.n7, n4=self.n7)

            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n3, self.n4])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n4, self.n7, self.n5])
            self.surface_tensor.append([-1, self.pid, self.n2, self.n3, self.n7, self.n5])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n5, self.n5])
            self.surface_tensor.append([-1, self.pid, self.n4, self.n3, self.n7, self.n7])

            self.format = "penta6"

        elif self.n4 != self.n5 and self.n5 != self.n6 and self.n6 != self.n7 and self.n7 != self.n8:
            self.surface[-1] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n3, n4=self.n4)
            self.surface[-2] = ElementShell(uid=-1, pid=self.pid, n1=self.n5, n2=self.n6, n3=self.n7, n4=self.n8)
            self.surface[-3] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n2, n3=self.n6, n4=self.n5)
            self.surface[-4] = ElementShell(uid=-1, pid=self.pid, n1=self.n2, n2=self.n3, n3=self.n7, n4=self.n6)
            self.surface[-5] = ElementShell(uid=-1, pid=self.pid, n1=self.n3, n2=self.n4, n3=self.n8, n4=self.n7)
            self.surface[-6] = ElementShell(uid=-1, pid=self.pid, n1=self.n1, n2=self.n5, n3=self.n8, n4=self.n4)

            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n3, self.n4])
            self.surface_tensor.append([-1, self.pid, self.n5, self.n6, self.n7, self.n8])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n2, self.n6, self.n5])
            self.surface_tensor.append([-1, self.pid, self.n2, self.n3, self.n7, self.n6])
            self.surface_tensor.append([-1, self.pid, self.n3, self.n4, self.n8, self.n7])
            self.surface_tensor.append([-1, self.pid, self.n1, self.n5, self.n8, self.n4])

            self.format = "hex8"

    def __repr__(self):
        return (f"element solid id: {self.uid}, "
                f"part id: {self.pid}, "
                f"node_id_1: {self.n1}, "
                f"node_id_2: {self.n2}, "
                f"node_id_3: {self.n3}, "
                f"node_id_4: {self.n4}, "
                f"node_id_5: {self.n5}, "
                f"node_id_6: {self.n6}, "
                f"node_id_7: {self.n7}, "
                f"node_id_8: {self.n8}\n")
