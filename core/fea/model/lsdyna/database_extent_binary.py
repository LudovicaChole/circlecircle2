from abc import ABC, abstractmethod


class DatabaseExtentBinary(ABC):
    """
    user define DatabaseExtentBinary() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.neiph = kwargs.get("neiph", args[1] if len(args) > 1 else 0)
        self.neips = kwargs.get("neips", args[2] if len(args) > 2 else 0)
        self.maxint = kwargs.get("maxint", args[3] if len(args) > 3 else 0)
        self.strflg = kwargs.get("strflg", args[4] if len(args) > 4 else 0)
        self.sigflg = kwargs.get("sigflg", args[5] if len(args) > 5 else 0)
        self.epsflg = kwargs.get("epsflg", args[6] if len(args) > 6 else 0)
        self.rltflg = kwargs.get("rltflg", args[7] if len(args) > 7 else 0)
        self.engflg = kwargs.get("engflg", args[8] if len(args) > 8 else 0)
        self.cmpflg = kwargs.get("cmpflg", args[9] if len(args) > 9 else 0)
        self.ieverp = kwargs.get("ieverp", args[10] if len(args) > 10 else 0)
        self.beamip = kwargs.get("beamip", args[11] if len(args) > 11 else 0)
        self.dcomp = kwargs.get("dcomp", args[12] if len(args) > 12 else 0)
        self.shge = kwargs.get("shge", args[13] if len(args) > 13 else 0)
        self.stssz = kwargs.get("stssz", args[14] if len(args) > 14 else 0)
        self.n3thdt = kwargs.get("n3thdt", args[15] if len(args) > 15 else 0)
        self.ialemat = kwargs.get("ialemat", args[16] if len(args) > 16 else 0)

        self.name = kwargs.get("name", args[17] if len(args) > 17 else "default")

        if self.name == "default":
            self.name = f"database_extent_binary_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"database_extent_binary id: {self.uid}, "
                    f"neiph: {self.neiph}, "
                    f"neips: {self.neips}, "
                    f"maxint: {self.maxint}, "
                    f"strflg: {self.strflg}, "
                    f"sigflg: {self.sigflg}, "
                    f"epsflg: {self.epsflg}, "
                    f"rltflg: {self.rltflg}, "
                    f"engflg: {self.engflg}, "
                    f"cmpflg: {self.cmpflg}, "
                    f"ieverp: {self.ieverp}, "
                    f"beamip: {self.beamip}, "
                    f"dcomp: {self.dcomp}, "
                    f"shge: {self.shge}, "
                    f"stssz: {self.stssz}, "
                    f"n3thdt: {self.n3thdt}, "
                    f"ialemat: {self.ialemat}\n")

        else:
            return (f"database_extent_binary name: {self.name}"
                    f"database_extent_binary id: {self.uid}, "
                    f"neiph: {self.neiph}, "
                    f"neips: {self.neips}, "
                    f"maxint: {self.maxint}, "
                    f"strflg: {self.strflg}, "
                    f"sigflg: {self.sigflg}, "
                    f"epsflg: {self.epsflg}, "
                    f"rltflg: {self.rltflg}, "
                    f"engflg: {self.engflg}, "
                    f"cmpflg: {self.cmpflg}, "
                    f"ieverp: {self.ieverp}, "
                    f"beamip: {self.beamip}, "
                    f"dcomp: {self.dcomp}, "
                    f"shge: {self.shge}, "
                    f"stssz: {self.stssz}, "
                    f"n3thdt: {self.n3thdt}, "
                    f"ialemat: {self.ialemat}\n")