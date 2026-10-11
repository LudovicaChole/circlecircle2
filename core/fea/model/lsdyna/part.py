from abc import ABC, abstractmethod


class Part(ABC):
    """
    user define Part() object
    input 6 parameters: name, uid, secid, mid, eosid, hgid
    """

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", args[0] if len(args) > 0 else 0)
        self.uid = kwargs.get("uid", args[1] if len(args) > 1 else 0)
        self.secid = kwargs.get("secid", args[2] if len(args) > 2 else 0)
        self.mid = kwargs.get("mid", args[3] if len(args) > 3 else 0)
        self.eosid = kwargs.get("eosid", args[4] if len(args) > 4 else 0)
        self.hgid = kwargs.get("hgid", args[5] if len(args) > 5 else 0)
        self.grav = kwargs.get("grav", args[6] if len(args) > 6 else 0)
        self.adpopt = kwargs.get("adpopt", args[7] if len(args) > 7 else 0)
        self.tmid = kwargs.get("tmid", args[8] if len(args) > 8 else 0)
        self.xc = kwargs.get("xc", args[9] if len(args) > 9 else 0)
        self.yc = kwargs.get("yc", args[10] if len(args) > 10 else 0)
        self.zc = kwargs.get("zc", args[11] if len(args) > 11 else 0)
        self.tm = kwargs.get("tm", args[12] if len(args) > 12 else 0)
        self.ircs = kwargs.get("ircs", args[13] if len(args) > 13 else 0)
        self.nodeid = kwargs.get("nodeid", args[14] if len(args) > 14 else 0)
        self.ixx = kwargs.get("ixx", args[15] if len(args) > 15 else 0)
        self.ixy = kwargs.get("ixy", args[16] if len(args) > 16 else 0)
        self.ixz = kwargs.get("ixz", args[17] if len(args) > 17 else 0)
        self.iyy = kwargs.get("iyy", args[18] if len(args) > 18 else 0)
        self.iyz = kwargs.get("iyz", args[19] if len(args) > 19 else 0)
        self.izz = kwargs.get("izz", args[20] if len(args) > 20 else 0)
        self.vtx = kwargs.get("vtx", args[21] if len(args) > 21 else 0)
        self.vty = kwargs.get("vty", args[22] if len(args) > 22 else 0)
        self.vtz = kwargs.get("vtz", args[23] if len(args) > 23 else 0)
        self.vrx = kwargs.get("vrx", args[24] if len(args) > 24 else 0)
        self.vry = kwargs.get("vry", args[25] if len(args) > 25 else 0)
        self.vrz = kwargs.get("vrx", args[26] if len(args) > 26 else 0)

    def __repr__(self):
        if self.tm == 0:
            return (f"part name: {self.name}\n"
                    f"part id: {self.uid}, "
                    f"section id: {self.secid}, "
                    f"material id: {self.mid}, "
                    f"eos id: {self.eosid}, "
                    f"hourglass id: {self.hgid}\n")
        else:
            return (f"part name: {self.name}\n"
                    f"part id: {self.uid}, "
                    f"section id: {self.secid}, "
                    f"material id: {self.mid}, "
                    f"eos id: {self.eosid}, "
                    f"hourglass id: {self.hgid}, "
                    f"gravity: {self.grav}, "
                    f"adpopt: {self.adpopt}, "
                    f"tmid: {self.tmid}, "
                    f"xc: {self.xc}, "
                    f"yc: {self.yc}, "
                    f"zc: {self.zc}, "
                    f"tm: {self.tm}, "
                    f"ircs: {self.ircs}, "
                    f"nodeid: {self.nodeid}, "
                    f"ixx: {self.ixx}, "
                    f"ixy: {self.ixy}, "
                    f"ixz: {self.ixz}, "
                    f"iyy: {self.iyy}, "
                    f"iyz: {self.iyz}, "
                    f"izz: {self.izz}, "
                    f"vtx: {self.vtx}, "
                    f"vty: {self.vty}, "
                    f"vtz: {self.vtz}, "
                    f"vrx: {self.vrx}, "
                    f"vry: {self.vry}, "
                    f"vrz: {self.vrz}\n")
