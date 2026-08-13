from abc import ABC, abstractmethod


class SecFo(ABC):
    """
    user define SecFo() object
    input 4 parameters:
    Samples:

    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.idsf = kwargs.get("idsf", args[1] if len(args) > 1 else None)
        self.ntyp = kwargs.get("ntyp", args[2] if len(args) > 2 else None)
        self.ifra = kwargs.get("ifra", args[3] if len(args) > 3 else None)
        self.name = kwargs.get("name", args[4] if len(args) > 4 else None)

        self.entity_selection = {
            "nod": set(),
            "ele": set(),
        }

    def __repr__(self):
        return (f"uid: {self.uid}, "
                f"idsf: {self.idsf}, "
                f"ntyp: {self.ntyp}, "
                f"ifra: {self.ifra}, "
                f"name: {self.name}, "
                f"entity_selection: {self.entity_selection}\n")
