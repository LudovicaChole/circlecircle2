from abc import ABC, abstractmethod


class Shell(ABC):
    """
    user define Shell() object
    input 4 parameters:
    Samples:
    $#          IDEL   IDPRT  IDNOD1  IDNOD2  IDNOD3  IDNOD4               H
    SHELL / 31004750  310003310211173102111531021109                     0.0
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.idel = kwargs.get("idel", args[1] if len(args) > 1 else None)
        self.idprt = kwargs.get("idprt", args[2] if len(args) > 2 else None)
        self.idnod1 = kwargs.get("idnod1", args[3] if len(args) > 3 else None)
        self.idnod2 = kwargs.get("idnod2", args[4] if len(args) > 4 else None)
        self.idnod3 = kwargs.get("idnod3", args[5] if len(args) > 5 else None)
        self.idnod4 = kwargs.get("idnod4", args[6] if len(args) > 6 else None)
        self.h = kwargs.get("h", args[7] if len(args) > 7 else None)

    def __repr__(self):
        return (f"shell id: {self.uid}, "
                f"idel: {self.idel}, "
                f"idprt: {self.idprt}, "
                f"idnod1: {self.idnod1}, "
                f"idnod2: {self.idnod2}, "
                f"idnod3: {self.idnod3}, "
                f"idnod4: {self.idnod4}, "
                f"h: {self.h}\n")
