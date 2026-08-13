from abc import ABC, abstractmethod


class Tetr4(ABC):
    """
    user define Tetr4() object
    input 4 parameters:
    Samples:

    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.idel = kwargs.get("idel", args[1] if len(args) > 1 else None)
        self.idprt = kwargs.get("idprt", args[2] if len(args) > 2 else None)
        self.idnod1 = kwargs.get("idnod1", args[3] if len(args) > 3 else None)
        self.idnod2 = kwargs.get("idnod2", args[4] if len(args) > 4 else None)
        self.idnod3 = kwargs.get("idnod3", args[5] if len(args) > 5 else None)
        self.idnod4 = kwargs.get("idnod4", args[6] if len(args) > 6 else None)
        self.tag = kwargs.get("tag", args[8] if len(args) > 8 else None)

    def __repr__(self):
        return (f"tetr4 id: {self.uid}, "
                f"idel: {self.idel}, "
                f"idprt: {self.idprt}, "
                f"idnod1: {self.idnod1}, "
                f"idnod2: {self.idnod2}, "
                f"idnod3: {self.idnod3}, "
                f"idnod4: {self.idnod4}, "
                f"tag: {self.tag}\n")
