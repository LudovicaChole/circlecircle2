from abc import ABC, abstractmethod


class DatabaseNodout(ABC):
    """
    user define DatabaseNodout() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.dt = kwargs.get("dt", args[1] if len(args) > 1 else 0)
        self.binary = kwargs.get("binary", args[2] if len(args) > 2 else 0)
        self.lcur = kwargs.get("lcur", args[3] if len(args) > 3 else 0)
        self.ioopt = kwargs.get("ioopt", args[4] if len(args) > 4 else 0)
        self.dthf = kwargs.get("dthf", args[5] if len(args) > 5 else 0)
        self.binhf = kwargs.get("binhf", args[6] if len(args) > 6 else 0)

        self.name = kwargs.get("name", args[7] if len(args) > 7 else "default")

        if self.name == "default":
            self.name = f"database_nodout_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"database_nodout id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"binary: {self.binary}, "
                    f"lcur: {self.lcur}, "
                    f"ioopt: {self.ioopt}, "
                    f"dthf: {self.dthf}, "
                    f"binhf: {self.binhf}\n")

        else:
            return (f"database_nodout name: {self.name}"
                    f"database_nodout id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"binary: {self.binary}, "
                    f"lcur: {self.lcur}, "
                    f"ioopt: {self.ioopt}, "
                    f"dthf: {self.dthf}, "
                    f"binhf: {self.binhf}\n")