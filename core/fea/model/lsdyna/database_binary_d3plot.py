from abc import ABC, abstractmethod


class DatabaseBinaryD3plot(ABC):
    """
    user define DatabaseBinaryD3plot() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.dt = kwargs.get("dt", args[1] if len(args) > 1 else 0)
        self.lcdt = kwargs.get("lcdt", args[2] if len(args) > 2 else 0)
        self.beam = kwargs.get("beam", args[3] if len(args) > 3 else 0)
        self.npltc = kwargs.get("npltc", args[4] if len(args) > 4 else 0)
        self.psepid = kwargs.get("psepid", args[5] if len(args) > 5 else 0)
        self.ioopt = kwargs.get("ioopt", args[6] if len(args) > 6 else 0)
        self.rate = kwargs.get("rate", args[7] if len(args) > 7 else 0)
        self.cutoff = kwargs.get("cutoff", args[8] if len(args) > 8 else 0)
        self.window = kwargs.get("window", args[9] if len(args) > 9 else 0)
        self.ptype = kwargs.get("ptype", args[10] if len(args) > 10 else 0)
        self.pset = kwargs.get("pset", args[11] if len(args) > 11 else 0)

        self.name = kwargs.get("name", args[12] if len(args) > 12 else "default")

        if self.name == "default":
            self.name = f"database_binary_intfor_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"database_binary_d3plot id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"lcdt: {self.lcdt}, "
                    f"beam: {self.beam}, "
                    f"npltc: {self.npltc}, "
                    f"psepid: {self.psepid}, "
                    f"ioopt: {self.ioopt}, "
                    f"rate: {self.rate}, "
                    f"cutoff: {self.cutoff}, "
                    f"window: {self.window}, "
                    f"type: {self.ptype}, "
                    f"pset: {self.pset}\n")

        else:
            return (f"database_binary_d3plot name: {self.name}"
                    f"database_binary_d3plot id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"lcdt: {self.lcdt}, "
                    f"beam: {self.beam}, "
                    f"npltc: {self.npltc}, "
                    f"psepid: {self.psepid}, "
                    f"ioopt: {self.ioopt}, "
                    f"rate: {self.rate}, "
                    f"cutoff: {self.cutoff}, "
                    f"window: {self.window}, "
                    f"type: {self.ptype}, "
                    f"pset: {self.pset}\n")