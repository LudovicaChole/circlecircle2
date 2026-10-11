from abc import ABC, abstractmethod


class ControlTimestep(ABC):
    """
    user define ControlTimestep() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.dtinit = kwargs.get("dtinit", args[1] if len(args) > 1 else 0)
        self.tssfac = kwargs.get("tssfac", args[2] if len(args) > 2 else 0)
        self.isdo = kwargs.get("isdo", args[3] if len(args) > 3 else 0)
        self.tslimt = kwargs.get("tslimt", args[4] if len(args) > 4 else 0)
        self.dt2ms = kwargs.get("dt2ms", args[5] if len(args) > 5 else 0)
        self.lctm = kwargs.get("lctm", args[6] if len(args) > 6 else 0)
        self.erode = kwargs.get("erode", args[7] if len(args) > 7 else 0)
        self.ms1st = kwargs.get("ms1st", args[8] if len(args) > 8 else 0)
        # Optional card 2 has a different layout; columns 4, 5 and 7 are unused.
        self.dt2msf = kwargs.get('dt2msf', 0.0)
        self.dt2mslc = kwargs.get('dt2mslc', 0)
        self.imscl = kwargs.get('imscl', 0)
        self.rmscl = kwargs.get('rmscl', 0.0)
        self.ihdo = kwargs.get('ihdo', 0)
        self.has_optional_card = False

        self.name = kwargs.get("name", args[9] if len(args) > 9 else "default")

        if self.name == "default":
            self.name = f"control_timestep_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_timestep id: {self.uid}, "
                    f"dtinit: {self.dtinit}, "
                    f"tssfac: {self.tssfac}, "
                    f"isdo: {self.isdo}, "
                    f"tslimt: {self.tslimt}, "
                    f"dt2ms: {self.dt2ms}, "
                    f"lctm: {self.lctm}, "
                    f"erode: {self.erode}, "
                    f"ms1st: {self.ms1st}\n")

        else:
            return (f"control_timestep name: {self.name}"
                    f"control_timestep id: {self.uid}, "
                    f"dtinit: {self.dtinit}, "
                    f"tssfac: {self.tssfac}, "
                    f"isdo: {self.isdo}, "
                    f"tslimt: {self.tslimt}, "
                    f"dt2ms: {self.dt2ms}, "
                    f"lctm: {self.lctm}, "
                    f"erode: {self.erode}, "
                    f"ms1st: {self.ms1st}\n")
