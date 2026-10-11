from abc import ABC, abstractmethod


class SectionShell(ABC):
    """
    user define SectionShell() object
    input 9 parameters: uid, elform, shrf, nip, t1, t2, t3, t4, name
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.elform = kwargs.get("elform", args[1] if len(args) > 1 else 16)
        self.shrf = kwargs.get("shrf", args[2] if len(args) > 2 else 0.833)
        self.nip = kwargs.get("nip", args[3] if len(args) > 3 else 5)
        self.t1 = kwargs.get("t1", args[4] if len(args) > 4 else 0)
        self.t2 = kwargs.get("t2", args[5] if len(args) > 5 else 0)
        self.t3 = kwargs.get("t3", args[6] if len(args) > 6 else 0)
        self.t4 = kwargs.get("t4", args[7] if len(args) > 7 else 0)

        self.name = kwargs.get("name", args[8] if len(args) > 8 else "default")

        if self.name == "default":
            self.name = f"p_shell_{self.t1}"

    def __repr__(self):
        if self.name == "default":
            return (f"section shell id: {self.uid}, "
                    f"elform: {self.elform}, "
                    f"shrf: {self.shrf}, "
                    f"nip: {self.nip}, "
                    f"t1: {self.t1}, "
                    f"t2: {self.t2}, "
                    f"t3: {self.t3}, "
                    f"t4: {self.t4}\n")

        else:
            return (f"section shell name: {self.name}, "
                    f"section shell id: {self.uid}, "
                    f"elform: {self.elform}, "
                    f"shrf: {self.shrf}, "
                    f"nip: {self.nip}, "
                    f"t1: {self.t1}, "
                    f"t2: {self.t2}, "
                    f"t3: {self.t3}, "
                    f"t4: {self.t4}\n")
