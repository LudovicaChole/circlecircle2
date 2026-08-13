from abc import ABC, abstractmethod


class Solid(ABC):
    """
    user define Tetr4() object
    input 4 parameters:
    Samples:
    $#          IDEL   IDPRT
    $#                IDNOD1  IDNOD2  IDNOD3  IDNOD4  IDNOD5  IDNOD6  IDNOD7  IDNOD8
    SOLID / 31054155  310028
                    3100042531000424310003033100030431000423310004233100030231000302
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.idel = kwargs.get("idel", args[1] if len(args) > 1 else None)
        self.idprt = kwargs.get("idprt", args[2] if len(args) > 2 else None)
        self.idnod1 = kwargs.get("idnod1", args[3] if len(args) > 3 else None)
        self.idnod2 = kwargs.get("idnod2", args[4] if len(args) > 4 else None)
        self.idnod3 = kwargs.get("idnod3", args[5] if len(args) > 5 else None)
        self.idnod4 = kwargs.get("idnod4", args[6] if len(args) > 6 else None)
        self.idnod5 = kwargs.get("idnod5", args[7] if len(args) > 7 else None)
        self.idnod6 = kwargs.get("idnod6", args[8] if len(args) > 8 else None)
        self.idnod7 = kwargs.get("idnod7", args[9] if len(args) > 9 else None)
        self.idnod8 = kwargs.get("idnod8", args[10] if len(args) > 10 else None)
        self.tag = kwargs.get("tag", args[11] if len(args) > 11 else None)

    def __repr__(self):
        return (f"solid id: {self.uid}, "
                f"idel: {self.idel}, "
                f"idprt: {self.idprt}, "
                f"idnod1: {self.idnod1}, "
                f"idnod2: {self.idnod2}, "
                f"idnod3: {self.idnod3}, "
                f"idnod4: {self.idnod4}, "
                f"idnod5: {self.idnod5}, "
                f"idnod6: {self.idnod6}, "
                f"idnod7: {self.idnod7}, "
                f"idnod8: {self.idnod8}, "
                f"tag: {self.tag}\n")
