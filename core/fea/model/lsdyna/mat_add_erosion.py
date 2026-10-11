from abc import ABC, abstractmethod


class MatAddErosion(ABC):
    """
    user define MatAddErosion() object
    input 8 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.excl = kwargs.get("excl", args[1] if len(args) > 1 else 0)
        self.mxpres = kwargs.get("mxpres", args[2] if len(args) > 2 else 0)
        self.mneps = kwargs.get("mneps", args[3] if len(args) > 3 else 0)
        self.effeps = kwargs.get("effeps", args[4] if len(args) > 4 else 0)
        self.voleps = kwargs.get("voleps", args[5] if len(args) > 5 else 0)
        self.numfip = kwargs.get("numfip", args[6] if len(args) > 6 else 0)
        self.ncs = kwargs.get("ncs", args[7] if len(args) > 7 else 0)
        self.mnpres = kwargs.get("mnpres", args[8] if len(args) > 8 else 0)
        self.sigp1 = kwargs.get("sigp1", args[9] if len(args) > 9 else 0)
        self.sigvm = kwargs.get("sigvm", args[10] if len(args) > 10 else 0)
        self.mxeps = kwargs.get("mxeps", args[11] if len(args) > 11 else 0)
        self.epssh = kwargs.get("epssh", args[12] if len(args) > 12 else 0)
        self.sigth = kwargs.get("sigth", args[13] if len(args) > 13 else 0)
        self.impulse = kwargs.get("impulse", args[14] if len(args) > 14 else 0)
        self.failtm = kwargs.get("failtm", args[15] if len(args) > 15 else 0)
        self.idam = kwargs.get("idam", args[16] if len(args) > 16 else 0)
        self.dmgtyp = kwargs.get("dmgtyp", args[17] if len(args) > 17 else 0)
        self.lcsdg = kwargs.get("lcsdg", args[18] if len(args) > 18 else 0)
        self.ecrit = kwargs.get("ecrit", args[19] if len(args) > 19 else 0)
        self.dmgexp = kwargs.get("dmgexp", args[20] if len(args) > 20 else 0)
        self.dcrit = kwargs.get("dcrit", args[21] if len(args) > 21 else 0)
        self.fadexp = kwargs.get("fadexp", args[22] if len(args) > 22 else 0)
        self.lcregd = kwargs.get("lcregd", args[23] if len(args) > 23 else 0)
        self.sizflg = kwargs.get("sizflg", args[24] if len(args) > 24 else 0)
        self.refsz = kwargs.get("refsz", args[25] if len(args) > 25 else 0)
        self.nahsv = kwargs.get("nahsv", args[26] if len(args) > 26 else 0)
        self.lcsrs = kwargs.get("lcsrs", args[27] if len(args) > 27 else 0)
        self.shrf = kwargs.get("shrf", args[28] if len(args) > 28 else 0)
        self.biaxf = kwargs.get("biaxf", args[29] if len(args) > 29 else 0)

        self.name = kwargs.get("name", args[30] if len(args) > 30 else "default")

        for field in ("lcfld", "nsff", "epsthin", "engcrt", "radcrt", "lceps12", "lceps13", "lcepsmx", "dteflt", "volfrac", "mxtmp", "dtmin"):
            setattr(self, field, kwargs.get(field, 0))
        self.tag = "mat_add_erosion"

    def __repr__(self):
        if self.name == "default":
            return (f"mat add erosion id: {self.uid}, "
                    f"excl: {self.excl}, "
                    f"mxpres: {self.mxpres}, "
                    f"mneps: {self.mneps}, "
                    f"effeps: {self.effeps}, "
                    f"voleps: {self.voleps}, "
                    f"numfip: {self.numfip}, "
                    f"ncs: {self.ncs}, "
                    f"mnpres: {self.mnpres}, "
                    f"sigp1: {self.sigp1}, "
                    f"sigvm: {self.sigvm}, "
                    f"mxeps: {self.mxeps}, "
                    f"epssh: {self.epssh}, "
                    f"sigth: {self.sigth}, "
                    f"impulse: {self.impulse}, "
                    f"failtm: {self.failtm}, "
                    f"idam: {self.idam}, "
                    f"dmgtyp: {self.dmgtyp}, "
                    f"lcsdg: {self.lcsdg}, "
                    f"ecrit: {self.ecrit}, "
                    f"dmgexp: {self.dmgexp}, "
                    f"dcrit: {self.dcrit}, "
                    f"fadexp: {self.fadexp}, "
                    f"lcregd: {self.lcregd}, "
                    f"sizflg: {self.sizflg}, "
                    f"refsz: {self.refsz}. "
                    f"nahsv: {self.nahsv}, "
                    f"lcsrs: {self.lcsrs}, "
                    f"shrf: {self.shrf}, "
                    f"biaxf: {self.biaxf}\n")

        else:
            return (f"mat add erosion id: {self.uid}, "
                    f"excl: {self.excl}, "
                    f"mxpres: {self.mxpres}, "
                    f"mneps: {self.mneps}, "
                    f"effeps: {self.effeps}, "
                    f"voleps: {self.voleps}, "
                    f"numfip: {self.numfip}, "
                    f"ncs: {self.ncs}, "
                    f"mnpres: {self.mnpres}, "
                    f"sigp1: {self.sigp1}, "
                    f"sigvm: {self.sigvm}, "
                    f"mxeps: {self.mxeps}, "
                    f"epssh: {self.epssh}, "
                    f"sigth: {self.sigth}, "
                    f"impulse: {self.impulse}, "
                    f"failtm: {self.failtm}, "
                    f"idam: {self.idam}, "
                    f"dmgtyp: {self.dmgtyp}, "
                    f"lcsdg: {self.lcsdg}, "
                    f"ecrit: {self.ecrit}, "
                    f"dmgexp: {self.dmgexp}, "
                    f"dcrit: {self.dcrit}, "
                    f"fadexp: {self.fadexp}, "
                    f"lcregd: {self.lcregd}, "
                    f"sizflg: {self.sizflg}, "
                    f"refsz: {self.refsz}. "
                    f"nahsv: {self.nahsv}, "
                    f"lcsrs: {self.lcsrs}, "
                    f"shrf: {self.shrf}, "
                    f"biaxf: {self.biaxf}, "
                    f"name: {self.name}\n")
