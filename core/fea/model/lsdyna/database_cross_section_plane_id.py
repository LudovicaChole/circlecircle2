from abc import ABC, abstractmethod


class DatabaseCrossSectionPlaneID(ABC):
    """
    user defined DatabaseCrossSectionPlaneID() object
    input 4 parameters:
    """
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.psid = kwargs.get("psid", args[1] if len(args) > 1 else 0)
        self.xct = kwargs.get("xct", args[2] if len(args) > 2 else 0)
        self.yct = kwargs.get("yct", args[3] if len(args) > 3 else 0)
        self.zct = kwargs.get("zct", args[4] if len(args) > 4 else 0)
        self.xch = kwargs.get("xch", args[5] if len(args) > 5 else 0)
        self.ych = kwargs.get("ych", args[6] if len(args) > 6 else 0)
        self.zch = kwargs.get("zch", args[7] if len(args) > 7 else 0)
        self.radius = kwargs.get("radius", args[8] if len(args) > 8 else 0)
        self.xhev = kwargs.get("xhev", args[9] if len(args) > 9 else 0)
        self.yhev = kwargs.get("yhev", args[10] if len(args) > 10 else 0)
        self.zhev = kwargs.get("zhev", args[11] if len(args) > 11 else 0)
        self.lenl = kwargs.get("lenl", args[12] if len(args) > 12 else 0)
        self.lenm = kwargs.get("lenm", args[13] if len(args) > 13 else 0)
        self.did = kwargs.get("did", args[14] if len(args) > 14 else 0)
        self.itype = kwargs.get("itype", args[15] if len(args) > 15 else 0)

        self.name = kwargs.get("name", args[16] if len(args) > 16 else "default")

        self.pset = None

    def __repr__(self):
        if self.name == "default":
            return (f"database cross section plane id: {self.uid}, "
                    f"psid: {self.psid}, "
                    f"xct: {self.xct}, "
                    f"yct: {self.yct}, "
                    f"zct: {self.zct}, "
                    f"xch: {self.xch}, "
                    f"ych: {self.ych}, "
                    f"zch: {self.zch}, "
                    f"radius: {self.radius}, "
                    f"xhev: {self.xhev}, "
                    f"yhev: {self.yhev}, "
                    f"zhev: {self.zhev}, "
                    f"lenl: {self.lenl}, "
                    f"lenm: {self.lenm}, "
                    f"did: {self.did}, "
                    f"itype: {self.itype}\n")

        else:
            return (f"database cross section plane id: {self.uid}, "
                    f"psid: {self.psid}, "
                    f"xct: {self.xct}, "
                    f"yct: {self.yct}, "
                    f"zct: {self.zct}, "
                    f"xch: {self.xch}, "
                    f"ych: {self.ych}, "
                    f"zch: {self.zch}, "
                    f"radius: {self.radius}, "
                    f"xhev: {self.xhev}, "
                    f"yhev: {self.yhev}, "
                    f"zhev: {self.zhev}, "
                    f"lenl: {self.lenl}, "
                    f"lenm: {self.lenm}, "
                    f"did: {self.did}, "
                    f"itype: {self.itype}, "
                    f"name: {self.name}\n")
