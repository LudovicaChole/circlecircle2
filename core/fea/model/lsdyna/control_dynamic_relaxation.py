from abc import ABC, abstractmethod


class ControlDynamicRelaxation(ABC):
    """
    user define ControlDynamicRelaxation() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.nrcyck = kwargs.get("nrcyck", args[1] if len(args) > 1 else 0)
        self.drtol = kwargs.get("drtol", args[2] if len(args) > 2 else 0)
        self.drfctr = kwargs.get("drfctr", args[3] if len(args) > 3 else 0)
        self.drterm = kwargs.get("drterm", args[4] if len(args) > 4 else 0)
        self.tssfdr = kwargs.get("tssfdr", args[5] if len(args) > 5 else 0)
        self.irelal = kwargs.get("irelal", args[6] if len(args) > 6 else 0)
        self.edttl = kwargs.get("edttl", args[7] if len(args) > 7 else 0)
        self.idrflg = kwargs.get("idrflg", args[8] if len(args) > 8 else 0)

        self.name = kwargs.get("name", args[9] if len(args) > 9 else "default")

        if self.name == "default":
            self.name = f"control_dynamic_relaxation_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_dynamic_relaxation id: {self.uid}, "
                    f"nrcyck: {self.nrcyck}, "
                    f"drtol: {self.drtol}, "
                    f"drfctr: {self.drfctr}, "
                    f"drterm: {self.drterm}, "
                    f"tssfdr: {self.tssfdr}, "
                    f"irelal: {self.irelal},"
                    f"edttl: {self.edttl},"
                    f"idrflg: {self.idrflg}\n")

        else:
            return (f"control_dynamic_relaxation name: {self.name}, "
                    f"control_dynamic_relaxation id: {self.uid}, "
                    f"nrcyck: {self.nrcyck}, "
                    f"drtol: {self.drtol}, "
                    f"drfctr: {self.drfctr}, "
                    f"drterm: {self.drterm}, "
                    f"tssfdr: {self.tssfdr}, "
                    f"irelal: {self.irelal},"
                    f"edttl: {self.edttl},"
                    f"idrflg: {self.idrflg}\n")