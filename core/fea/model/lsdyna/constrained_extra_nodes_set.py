from abc import ABC, abstractmethod


class ConstrainedExtraNodesSet(ABC):
    """
    user defined ConstrainedExtraNodesSet() object
    input 4 parameters:
    """
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.pid = kwargs.get("pid", args[1] if len(args) > 1 else 0)
        self.nsid = kwargs.get("nsid", args[2] if len(args) > 2 else 0)
        self.iflag = kwargs.get("iflag", args[3] if len(args) > 3 else 0)

        self.name = kwargs.get("name", args[4] if len(args) > 4 else "default")

        self.nset = None

    def __repr__(self):
        if self.name == "default":
            return (f"constrained extra nodes set id: {self.uid}, "
                    f"pid: {self.pid}, "
                    f"nsid: {self.nsid}, "
                    f"iflag: {self.iflag}\n")

        else:
            return (f"constrained extra nodes set id: {self.uid}, "
                    f"pid: {self.pid}, "
                    f"nsid: {self.nsid}, "
                    f"iflag: {self.iflag}, "
                    f"name: {self.name}\n")
