from abc import ABC, abstractmethod


class DefineCurve(ABC):
    """
    user defined DefineCurve() object
    input 4 parameters: uid, pid, node_id_1, node_id_2, node_id_3, node_id_4
    """
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.sidr = kwargs.get("sidr", args[1] if len(args) > 1 else 0)
        self.sfa = kwargs.get("sfa", args[2] if len(args) > 2 else 0)
        self.sfo = kwargs.get("sfo", args[3] if len(args) > 3 else 0)
        self.offa = kwargs.get("offa", args[4] if len(args) > 4 else 0)
        self.offo = kwargs.get("offo", args[5] if len(args) > 5 else 0)
        self.dattyp = kwargs.get("dattyp", args[6] if len(args) > 6 else 0)
        self.lcint = kwargs.get("lcint", args[7] if len(args) > 7 else 0)

        self.name = kwargs.get("name", args[8] if len(args) > 8 else "default")

        self.a1 = []
        self.o1 = []

        self.tag = "curve"

        if self.name == "default":
            self.name = f"default_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"define curve id: {self.uid}, "
                    f"sidr: {self.sidr}, "
                    f"sfa: {self.sfa}, "
                    f"sfo: {self.sfo}, "
                    f"offa: {self.offa}, "
                    f"offo: {self.offo}, "
                    f"dattyp: {self.dattyp}, "
                    f"lcint: {self.lcint}\n")

        else:
            return (f"define curve id: {self.uid}, "
                    f"sidr: {self.sidr}, "
                    f"sfa: {self.sfa}, "
                    f"sfo: {self.sfo}, "
                    f"offa: {self.offa}, "
                    f"offo: {self.offo}, "
                    f"dattyp: {self.dattyp}, "
                    f"lcint: {self.lcint}, "
                    f"name: {self.name}\n")
