from abc import ABC, abstractmethod


class Pyvar(ABC):
    """
    user define Pyvar() object
    input 4 parameters: uid, x, y, z
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.pyvarid = kwargs.get("pyvarid", args[1] if len(args) > 1 else None)
        self.name = kwargs.get("name", args[2] if len(args) > 2 else None)
        self.value = kwargs.get("value", args[3] if len(args) > 3 else None)

    def __repr__(self):
        return (f"pyvar uid: {self.uid}, "
                f"pyvarid: {self.pyvarid}, "
                f"name: {self.name}, "
                f"value: {self.value}\n")
