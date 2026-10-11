from abc import ABC, abstractmethod


class DatabaseDeforc(ABC):
    """
    user define DatabaseDeforc() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.dt = kwargs.get("dt", args[1] if len(args) > 1 else 0)
        self.binary = kwargs.get("binary", args[2] if len(args) > 2 else 0)
        self.lcur = kwargs.get("lcur", args[3] if len(args) > 3 else 0)
        self.ioopt = kwargs.get("ioopt", args[4] if len(args) > 4 else 0)

        self.name = kwargs.get("name", args[5] if len(args) > 5 else "default")

        if self.name == "default":
            self.name = f"database_deforc_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"database_deforc id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"binary: {self.binary}, "
                    f"lcur: {self.lcur}, "
                    f"ioopt: {self.ioopt}\n")

        else:
            return (f"database_deforc name: {self.name}"
                    f"database_deforc id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"binary: {self.binary}, "
                    f"lcur: {self.lcur}, "
                    f"ioopt: {self.ioopt}\n")