from abc import ABC, abstractmethod


class ElementShell(ABC):
    """
    user defined element shell class
    input 4 parameters: uid, pid, node_id_1, node_id_2, node_id_3, node_id_4
    """
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.pid = kwargs.get("pid", args[1] if len(args) > 1 else None)
        self.n1 = kwargs.get("n1", args[2] if len(args) > 2 else None)
        self.n2 = kwargs.get("n2", args[3] if len(args) > 3 else None)
        self.n3 = kwargs.get("n3", args[4] if len(args) > 4 else None)
        self.n4 = kwargs.get("n4", args[5] if len(args) > 5 else None)

        self.format = None
        self.normal = None
        self.area = None
        self.warp = None
        self.edge = None
        self.max_edge = None
        self.min_edge = None

        self._check_element_info()

    def _check_element_info(self):
        if self.n3 == self.n4 or self.n4 == -1:
            self.format = "s3"
        else:
            self.format = "s4"

    def __repr__(self):
        return (f"element shell id: {self.uid}, "
                f"part id: {self.pid}, "
                f"node_id_1: {self.n1}, "
                f"node_id_2: {self.n2}, "
                f"node_id_3: {self.n3}, "
                f"node_id_4: {self.n4}\n")
