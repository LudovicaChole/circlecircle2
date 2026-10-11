from abc import ABC, abstractmethod


class ControlSolid(ABC):
    """
    user define ControlSolid() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.esort = kwargs.get("esort", args[1] if len(args) > 1 else 0)
        self.fmatrx = kwargs.get("fmatrx", args[2] if len(args) > 2 else 0)
        self.niptets = kwargs.get("niptets", args[3] if len(args) > 3 else 0)
        self.swlocl = kwargs.get("swlocl", args[4] if len(args) > 4 else 0)
        self.psfail = kwargs.get("psfail", args[5] if len(args) > 5 else 0)
        self.t10jtol = kwargs.get("t10jtol", args[6] if len(args) > 6 else 0)
        self.icoh = kwargs.get("icoh", args[7] if len(args) > 7 else 0)
        self.tet13k = kwargs.get("tet13k", args[8] if len(args) > 8 else 0)
        self.pm1 = kwargs.get("pm1", args[9] if len(args) > 9 else 0)
        self.pm2 = kwargs.get("pm2", args[10] if len(args) > 10 else 0)
        self.pm3 = kwargs.get("pm3", args[11] if len(args) > 11 else 0)
        self.pm4 = kwargs.get("pm4", args[12] if len(args) > 12 else 0)
        self.pm5 = kwargs.get("pm5", args[13] if len(args) > 13 else 0)
        self.pm6 = kwargs.get("pm6", args[14] if len(args) > 14 else 0)
        self.pm7 = kwargs.get("pm7", args[15] if len(args) > 15 else 0)
        self.pm8 = kwargs.get("pm8", args[16] if len(args) > 16 else 0)
        self.pm9 = kwargs.get("pm9", args[17] if len(args) > 17 else 0)
        self.pm10 = kwargs.get("pm10", args[18] if len(args) > 18 else 0)

        self.name = kwargs.get("name", args[19] if len(args) > 19 else "default")

        if self.name == "default":
            self.name = f"control_solid_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_solid id: {self.uid}, "
                    f"esort: {self.esort}, "
                    f"fmatrx: {self.fmatrx}, "
                    f"niptets: {self.niptets}, "
                    f"swlocl: {self.swlocl}, "
                    f"psfail: {self.psfail}, "
                    f"t10jtol: {self.t10jtol}, "
                    f"icoh: {self.icoh}, "
                    f"tet13k: {self.tet13k}, "
                    f"pm1: {self.pm1}, "
                    f"pm2: {self.pm2}, "
                    f"pm3: {self.pm3}, "
                    f"pm4: {self.pm4}, "
                    f"pm5: {self.pm5}, "
                    f"pm6: {self.pm6}, "
                    f"pm7: {self.pm7}, "
                    f"pm8: {self.pm8}, "
                    f"pm9: {self.pm9}, "
                    f"pm10: {self.pm10}\n")

        else:
            return (f"control_solid name: {self.name}, "
                    f"control_solid id: {self.uid}, "
                    f"esort: {self.esort}, "
                    f"fmatrx: {self.fmatrx}, "
                    f"niptets: {self.niptets}, "
                    f"swlocl: {self.swlocl}, "
                    f"psfail: {self.psfail}, "
                    f"t10jtol: {self.t10jtol}, "
                    f"icoh: {self.icoh}, "
                    f"tet13k: {self.tet13k}, "
                    f"pm1: {self.pm1}, "
                    f"pm2: {self.pm2}, "
                    f"pm3: {self.pm3}, "
                    f"pm4: {self.pm4}, "
                    f"pm5: {self.pm5}, "
                    f"pm6: {self.pm6}, "
                    f"pm7: {self.pm7}, "
                    f"pm8: {self.pm8}, "
                    f"pm9: {self.pm9}, "
                    f"pm10: {self.pm10}\n")
