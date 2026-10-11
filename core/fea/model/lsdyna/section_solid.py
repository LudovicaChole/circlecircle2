from abc import ABC, abstractmethod


class SectionSolid(ABC):
    """
    user define SectionSolid() object
    input 3 parameters: uid, elform, name
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.elform = kwargs.get("elform", args[1] if len(args) > 1 else 16)

        self.name = kwargs.get("name", args[2] if len(args) > 2 else "default")

        if self.name == "default":
            self.name = f"p_solid_{self.elform}"

    def __repr__(self):
        if self.name == "default":
            return (f"section solid id: {self.uid}, "
                    f"elform: {self.elform}\n")

        else:
            return (f"section solid name: {self.name}, "
                    f"section solid id: {self.uid}, "
                    f"elform: {self.elform}\n")
