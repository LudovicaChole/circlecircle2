from abc import ABC, abstractmethod


class ContactTiedNodesToSurfaceOffsetID(ABC):
    """
    user define ContactTiedNodesToSurfaceOffsetID() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.heading = kwargs.get("heading", args[1] if len(args) > 1 else 0)
        self.ssid = kwargs.get("ssid", args[2] if len(args) > 2 else 0)
        self.msid = kwargs.get("msid", args[3] if len(args) > 3 else 0)
        self.sstyp = kwargs.get("sstype", args[4] if len(args) > 4 else 0)
        self.mstyp = kwargs.get("mstype", args[5] if len(args) > 5 else 0)
        self.sboxid = kwargs.get("sboxid", args[6] if len(args) > 6 else 0)
        self.mboxid = kwargs.get("mboxid", args[7] if len(args) > 7 else 0)
        self.spr = kwargs.get("spr", args[8] if len(args) > 8 else 0)
        self.mpr = kwargs.get("mpr", args[9] if len(args) > 9 else 0)
        self.fs = kwargs.get("fs", args[10] if len(args) > 10 else 0)
        self.fd = kwargs.get("fd", args[11] if len(args) > 11 else 0)
        self.dc = kwargs.get("dc", args[12] if len(args) > 12 else 0)
        self.vc = kwargs.get("vc", args[13] if len(args) > 13 else 0)
        self.vdc = kwargs.get("vdc", args[14] if len(args) > 14 else 0)
        self.penchk = kwargs.get("penchk", args[15] if len(args) > 15 else 0)
        self.bt = kwargs.get("bt", args[16] if len(args) > 16 else 0)
        self.dt = kwargs.get("dt", args[17] if len(args) > 17 else 0)
        self.sfs = kwargs.get("sfs", args[18] if len(args) > 18 else 0)
        self.sfm = kwargs.get("sfm", args[19] if len(args) > 19 else 0)
        self.sst = kwargs.get("sst", args[20] if len(args) > 20 else 0)
        self.mst = kwargs.get("mst", args[21] if len(args) > 21 else 0)
        self.sfst = kwargs.get("sfst", args[22] if len(args) > 22 else 0)
        self.sfmt = kwargs.get("sfmt", args[23] if len(args) > 23 else 0)
        self.fsf = kwargs.get("fsf", args[24] if len(args) > 24 else 0)
        self.vsf = kwargs.get("vsf", args[25] if len(args) > 25 else 0)

        self.name = kwargs.get("name", args[26] if len(args) > 26 else "default")

        if self.name == "default":
            self.name = f"contact_tied_nodes_to_surface_offset_id_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"contact_tied_nodes_to_surface_offset_id id: {self.uid}, "
                    f"heading: {self.heading}, "
                    f"ssid: {self.ssid}, "
                    f"msid: {self.msid}, "
                    f"sstyp: {self.sstyp}, "
                    f"mstyp: {self.mstyp}, "
                    f"sboxid: {self.sboxid},"
                    f"mboxid: {self.mboxid},"
                    f"spr: {self.spr}, "
                    f"mpr: {self.mpr}, "
                    f"fs: {self.fs},"
                    f"fd: {self.fd},"
                    f"dc: {self.dc},"
                    f"vc: {self.vc},"
                    f"vdc: {self.vdc}, "
                    f"penchk: {self.penchk}, "
                    f"bt: {self.bt}, "
                    f"dt: {self.dt}, "
                    f"sfs: {self.sfs}, "
                    f"sfm: {self.sfm}, "
                    f"sst: {self.sst},"
                    f"mst: {self.mst}, "
                    f"sfst: {self.sfst}, "
                    f"sfmt: {self.sfmt}, "
                    f"fsf: {self.fsf}, "
                    f"vsf: {self.vsf}\n")

        else:
            return (f"contact_tied_nodes_to_surface_offset_id name: {self.name}, "
                    f"contact_tied_nodes_to_surface_offset_id id: {self.uid}, "
                    f"heading: {self.heading}, "
                    f"ssid: {self.ssid}, "
                    f"msid: {self.msid}, "
                    f"sstyp: {self.sstyp}, "
                    f"mstyp: {self.mstyp}, "
                    f"sboxid: {self.sboxid},"
                    f"mboxid: {self.mboxid},"
                    f"spr: {self.spr}, "
                    f"mpr: {self.mpr}, "
                    f"fs: {self.fs},"
                    f"fd: {self.fd},"
                    f"dc: {self.dc},"
                    f"vc: {self.vc},"
                    f"vdc: {self.vdc}, "
                    f"penchk: {self.penchk}, "
                    f"bt: {self.bt}, "
                    f"dt: {self.dt}, "
                    f"sfs: {self.sfs}, "
                    f"sfm: {self.sfm}, "
                    f"sst: {self.sst},"
                    f"mst: {self.mst}, "
                    f"sfst: {self.sfst}, "
                    f"sfmt: {self.sfmt}, "
                    f"fsf: {self.fsf}, "
                    f"vsf: {self.vsf}\n")
