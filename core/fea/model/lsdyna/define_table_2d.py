from abc import ABC, abstractmethod


class DefineTable2D(ABC):
    """
    user defined DefineTable2D() object
    input 4 parameters:
    """
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.sfa = kwargs.get("sfa", args[1] if len(args) > 1 else 0)
        self.offa = kwargs.get("offa", args[2] if len(args) > 2 else 0)

        self.name = kwargs.get("name", args[3] if len(args) > 3 else "default")

        self.value = []
        self.lcid = []

        self.tag = "table"

    def __repr__(self):
        if self.name == "default":
            return (f"define table id: {self.uid}, "
                    f"sfa: {self.sfa}, "
                    f"offa: {self.offa}\n")

        else:
            return (f"define curve id: {self.uid}, "
                    f"sfa: {self.sfa}, "
                    f"offa: {self.offa}, "
                    f"name: {self.name}\n")
