from abc import ABC, abstractmethod


class Hourglass(ABC):
    """
    user define Hourglass() object
    input 4 parameters: uid, x, y, z
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.ihq = kwargs.get("ihq", args[1] if len(args) > 1 else 0)
        self.qm = kwargs.get("qm", args[2] if len(args) > 2 else 0)
        self.ibq = kwargs.get("ibq", args[3] if len(args) > 3 else 0)
        self.q1 = kwargs.get("q1", args[4] if len(args) > 4 else 0)
        self.q2 = kwargs.get("q2", args[5] if len(args) > 5 else 0)
        self.qb = kwargs.get("qb", args[6] if len(args) > 6 else 0)
        self.qw = kwargs.get("qw", args[7] if len(args) > 7 else 0)

        self.name = kwargs.get("name", args[8] if len(args) > 8 else "default")

    def __repr__(self):
        if self.name == "default":
            return (f"hourglass id: {self.uid}, "
                    f"ihq: {self.ihq}, "
                    f"qm: {self.qm}, "
                    f"ibq: {self.ibq}, "
                    f"q1: {self.q1}, "
                    f"q2: {self.q2}, "
                    f"qb: {self.qb}, "
                    f"qw: {self.qw}\n")

        else:
            return (f"hourglass id: {self.uid}, "
                    f"ihq: {self.ihq}, "
                    f"qm: {self.qm}, "
                    f"ibq: {self.ibq}, "
                    f"q1: {self.q1}, "
                    f"q2: {self.q2}, "
                    f"qb: {self.qb}, "
                    f"qw: {self.qw}, "
                    f"name: {self.name}\n")
