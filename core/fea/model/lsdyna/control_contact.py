from abc import ABC, abstractmethod


class ControlContact(ABC):
    """
    user define ControlContact() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.slsfac = kwargs.get("slsfac", args[1] if len(args) > 1 else 0)
        self.rwpnal = kwargs.get("rwpna", args[2] if len(args) > 2 else 0)
        self.islchk = kwargs.get("islchk", args[3] if len(args) > 3 else 0)
        self.shlthk = kwargs.get("shlthk", args[4] if len(args) > 4 else 0)
        self.penopt = kwargs.get("penopt", args[5] if len(args) > 5 else 0)
        self.thkchg = kwargs.get("thkchg", args[6] if len(args) > 6 else 0)
        self.orien = kwargs.get("orien", args[7] if len(args) > 7 else 0)
        self.enmass = kwargs.get("enmass", args[8] if len(args) > 8 else 0)
        self.usrstr = kwargs.get("usrstr", args[9] if len(args) > 9 else 0)
        self.usrfrc = kwargs.get("usrfrc", args[10] if len(args) > 10 else 0)
        self.nsbcs = kwargs.get("nsbcs", args[11] if len(args) > 11 else 0)
        self.interm = kwargs.get("interm", args[12] if len(args) > 12 else 0)
        self.xpene = kwargs.get("xpene", args[13] if len(args) > 13 else 0)
        self.ssthk = kwargs.get("ssthk", args[14] if len(args) > 14 else 0)
        self.ecdt = kwargs.get("ecdt", args[15] if len(args) > 15 else 0)
        self.tiedprj = kwargs.get("tiedprj", args[16] if len(args) > 16 else 0)
        self.sfric = kwargs.get("sfric", args[17] if len(args) > 17 else 0)
        self.dfric = kwargs.get("dfric", args[18] if len(args) > 18 else 0)
        self.edc = kwargs.get("edc", args[19] if len(args) > 19 else 0)
        self.vfc = kwargs.get("vfc", args[20] if len(args) > 20 else 0)
        self.th = kwargs.get("th", args[21] if len(args) > 21 else 0)
        self.th_sf = kwargs.get("th_sf", args[22] if len(args) > 22 else 0)
        self.pen_sf = kwargs.get("pen_sf", args[23] if len(args) > 23 else 0)
        self.ptscl = kwargs.get("ptscl", args[24] if len(args) > 24 else 0)
        self.ignore = kwargs.get("ignore", args[25] if len(args) > 25 else 0)
        self.frceng = kwargs.get("frceng", args[26] if len(args) > 26 else 0)
        self.skiprwg = kwargs.get("skiprwg", args[27] if len(args) > 27 else 0)
        self.outseg = kwargs.get("outseg", args[28] if len(args) > 28 else 0)
        self.spotstp = kwargs.get("spotstp", args[29] if len(args) > 29 else 0)
        self.spotdel = kwargs.get("spotdel", args[30] if len(args) > 30 else 0)
        self.spothin = kwargs.get("spothin", args[31] if len(args) > 31 else 0)
        self.isym = kwargs.get("isym", args[32] if len(args) > 32 else 0)
        self.nserod = kwargs.get("nserod", args[33] if len(args) > 33 else 0)
        self.rwgaps = kwargs.get("rwgaps", args[34] if len(args) > 34 else 0)
        self.rwgdth = kwargs.get("rwgdth", args[35] if len(args) > 35 else 0)
        self.rwksf = kwargs.get("rwksf", args[36] if len(args) > 36 else 0)
        self.icov = kwargs.get("icov", args[37] if len(args) > 37 else 0)
        self.swradf = kwargs.get("swradf", args[38] if len(args) > 38 else 0)
        self.ithoff = kwargs.get("ithoff", args[39] if len(args) > 39 else 0)
        self.shledg = kwargs.get("shledg", args[40] if len(args) > 40 else 0)
        self.pstiff = kwargs.get("pstiff", args[41] if len(args) > 41 else 0)
        self.ithcnt = kwargs.get("ithcnt", args[42] if len(args) > 42 else 0)
        self.tdcnof = kwargs.get("tdcnof", args[43] if len(args) > 43 else 0)
        self.ftall = kwargs.get("ftall", args[44] if len(args) > 44 else 0)
        self.shltrw = kwargs.get("shltrw", args[45] if len(args) > 45 else 0)
        self.igactc = kwargs.get("igactc", args[46] if len(args) > 46 else 0)

        self.name = kwargs.get("name", args[9] if len(args) > 9 else "default")

        if self.name == "default":
            self.name = f"control_solution_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_contact id: {self.uid}, "
                    f"slsfac: {self.slsfac}, "
                    f"rwpnal: {self.rwpnal}, "
                    f"islchk: {self.islchk}, "
                    f"shlthk: {self.shlthk}, "
                    f"penopt: {self.penopt}, "
                    f"thkchg: {self.thkchg}, "
                    f"orien: {self.orien}, "
                    f"enmass: {self.enmass}, "
                    f"usrstr: {self.usrstr}, "
                    f"usrfrc: {self.usrfrc}, "
                    f"nsbcs: {self.nsbcs}, "
                    f"interm: {self.interm}, "
                    f"xpene: {self.xpene}, "
                    f"ssthk: {self.ssthk}, "
                    f"ecdt: {self.ecdt}, "
                    f"tiedprj: {self.tiedprj}, "
                    f"sfric: {self.sfric}, "
                    f"dfric: {self.dfric}, "
                    f"edc: {self.edc}, "
                    f"vfc: {self.vfc}, "
                    f"th: {self.th}, "
                    f"th_sf: {self.th_sf}, "
                    f"pen_sf: {self.pen_sf}, "
                    f"ptscl: {self.ptscl}, "
                    f"ignore: {self.ignore}, "
                    f"frceng: {self.frceng}, "
                    f"skiprwg: {self.skiprwg}, "
                    f"outseg: {self.outseg}, "
                    f"spotstp: {self.spotstp}, "
                    f"spotdel: {self.spotdel}, "
                    f"spothin: {self.spothin}, "
                    f"isym: {self.isym}, "
                    f"nserod: {self.nserod}, "
                    f"rwgaps: {self.rwgaps}, "
                    f"rwgdth: {self.rwgdth}, "
                    f"rwksf: {self.rwksf}, "
                    f"icov: {self.icov}, "
                    f"swradf: {self.swradf}, "
                    f"ithoff: {self.ithoff}, "
                    f"shledg: {self.shledg}, "
                    f"pstiff: {self.pstiff}, "
                    f"ithcnt: {self.ithcnt}, "
                    f"tdcnof: {self.tdcnof}, "
                    f"ftall: {self.ftall}, "
                    f"shltrw: {self.shltrw}, "
                    f"igactc: {self.igactc}\n")

        else:
            return (f"control_contact name: {self.name}"
                    f"control_contact id: {self.uid}, "
                    f"slsfac: {self.slsfac}, "
                    f"rwpnal: {self.rwpnal}, "
                    f"islchk: {self.islchk}, "
                    f"shlthk: {self.shlthk}, "
                    f"penopt: {self.penopt}, "
                    f"thkchg: {self.thkchg}, "
                    f"orien: {self.orien}, "
                    f"enmass: {self.enmass}, "
                    f"usrstr: {self.usrstr}, "
                    f"usrfrc: {self.usrfrc}, "
                    f"nsbcs: {self.nsbcs}, "
                    f"interm: {self.interm}, "
                    f"xpene: {self.xpene}, "
                    f"ssthk: {self.ssthk}, "
                    f"ecdt: {self.ecdt}, "
                    f"tiedprj: {self.tiedprj}, "
                    f"sfric: {self.sfric}, "
                    f"dfric: {self.dfric}, "
                    f"edc: {self.edc}, "
                    f"vfc: {self.vfc}, "
                    f"th: {self.th}, "
                    f"th_sf: {self.th_sf}, "
                    f"pen_sf: {self.pen_sf}, "
                    f"ptscl: {self.ptscl}, "
                    f"ignore: {self.ignore}, "
                    f"frceng: {self.frceng}, "
                    f"skiprwg: {self.skiprwg}, "
                    f"outseg: {self.outseg}, "
                    f"spotstp: {self.spotstp}, "
                    f"spotdel: {self.spotdel}, "
                    f"spothin: {self.spothin}, "
                    f"isym: {self.isym}, "
                    f"nserod: {self.nserod}, "
                    f"rwgaps: {self.rwgaps}, "
                    f"rwgdth: {self.rwgdth}, "
                    f"rwksf: {self.rwksf}, "
                    f"icov: {self.icov}, "
                    f"swradf: {self.swradf}, "
                    f"ithoff: {self.ithoff}, "
                    f"shledg: {self.shledg}, "
                    f"pstiff: {self.pstiff}, "
                    f"ithcnt: {self.ithcnt}, "
                    f"tdcnof: {self.tdcnof}, "
                    f"ftall: {self.ftall}, "
                    f"shltrw: {self.shltrw}, "
                    f"igactc: {self.igactc}\n")