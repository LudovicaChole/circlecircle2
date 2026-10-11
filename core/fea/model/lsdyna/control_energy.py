from abc import ABC, abstractmethod


class ControlEnergy(ABC):
    """
    user define ControlEnergy() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.hgen = kwargs.get("hgen", args[1] if len(args) > 1 else 0)
        self.rwen = kwargs.get("rwen", args[2] if len(args) > 2 else 0)
        self.slnten = kwargs.get("slnten", args[3] if len(args) > 3 else 0)
        self.rylen = kwargs.get("rylen", args[4] if len(args) > 4 else 0)
        self.irgen = kwargs.get("irgen", args[5] if len(args) > 5 else 0)

        self.name = kwargs.get("name", args[6] if len(args) > 6 else "default")

        if self.name == "default":
            self.name = f"control_energy_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_energy id: {self.uid}, "
                    f"hgen: {self.hgen}, "
                    f"rwen: {self.rwen}, "
                    f"slnten: {self.slnten}, "
                    f"rylen: {self.rylen}, "
                    f"irgen: {self.irgen}\n")

        else:
            return (f"control_energy name: {self.name}, "
                    f"control_energy id: {self.uid}, "
                    f"hgen: {self.hgen}, "
                    f"rwen: {self.rwen}, "
                    f"slnten: {self.slnten}, "
                    f"rylen: {self.rylen}, "
                    f"irgen: {self.irgen}\n")

