from abc import ABC, abstractmethod


class ControlShell(ABC):
    """
    user define ControlShell() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.wrpang = kwargs.get("wrpang", args[1] if len(args) > 1 else 0)
        self.esort = kwargs.get("esort", args[2] if len(args) > 2 else 0)
        self.irnxx = kwargs.get("irnxx", args[3] if len(args) > 3 else 0)
        self.istupd = kwargs.get("istupd", args[4] if len(args) > 4 else 0)
        self.theory = kwargs.get("theory", args[5] if len(args) > 5 else 0)
        self.bwc = kwargs.get("bwc", args[6] if len(args) > 6 else 0)
        self.miter = kwargs.get("miter", args[7] if len(args) > 7 else 0)
        self.proj = kwargs.get("proj", args[8] if len(args) > 8 else 0)
        self.rotascl = kwargs.get("rotascl", args[9] if len(args) > 9 else 0)
        self.intgrd = kwargs.get("intgrd", args[10] if len(args) > 10 else 0)
        self.lamsht = kwargs.get("lamsht", args[11] if len(args) > 11 else 0)
        self.cstyp6 = kwargs.get("cstyp6", args[12] if len(args) > 12 else 0)
        self.thshell = kwargs.get("thshell", args[13] if len(args) > 13 else 0)
        self.pstupd = kwargs.get("pstupd", args[14] if len(args) > 14 else 0)
        self.sidt4tu = kwargs.get("sidt4tu", args[15] if len(args) > 15 else 0)
        self.cntco = kwargs.get("cntco", args[16] if len(args) > 16 else 0)
        self.itsflg = kwargs.get("itsflg", args[17] if len(args) > 17 else 0)
        self.irquad = kwargs.get("irquad", args[18] if len(args) > 18 else 0)
        self.w_mode = kwargs.get("w_mode", args[19] if len(args) > 19 else 0)
        self.stretch = kwargs.get("stretch", args[20] if len(args) > 20 else 0)
        self.icrq = kwargs.get("icrq", args[21] if len(args) > 21 else 0)
        self.nfail1 = kwargs.get("nfail1", args[22] if len(args) > 22 else 0)
        self.nfail4 = kwargs.get("nfail4", args[23] if len(args) > 23 else 0)
        self.psnfail = kwargs.get("psnfail", args[24] if len(args) > 24 else 0)
        self.keepcs = kwargs.get("keepcs", args[25] if len(args) > 25 else 0)
        self.delfr = kwargs.get("delfr", args[26] if len(args) > 26 else 0)
        self.drcpsid = kwargs.get("drcpsid", args[27] if len(args) > 27 else 0)
        self.drcprm = kwargs.get("drcprm", args[28] if len(args) > 28 else 0)
        self.intperr = kwargs.get("intperr", args[29] if len(args) > 29 else 0)

        self.name = kwargs.get("name", args[5] if len(args) > 5 else "default")

        if self.name == "default":
            self.name = f"control_shell_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_shell id: {self.uid}, "
                    f"wrpang: {self.wrpang}, "
                    f"esort: {self.esort}, "
                    f"irnxx: {self.irnxx}, "
                    f"istupd: {self.istupd}, "
                    f"theory: {self.theory},"
                    f"bwc: {self.bwc}, "
                    f"miter: {self.miter}, "
                    f"proj: {self.proj}, "
                    f"rotascl: {self.rotascl},"
                    f"intgrd: {self.intgrd}, "
                    f"lamsht: {self.lamsht}, "
                    f"cstyp6: {self.cstyp6}, "
                    f"thshell: {self.thshell}, "
                    f"pstupd: {self.pstupd}, "
                    f"sidt4tu: {self.sidt4tu}, "
                    f"cntco: {self.cntco}, "
                    f"itsflg: {self.itsflg}, "
                    f"irquad: {self.irquad}, "
                    f"w_mode: {self.w_mode}, "
                    f"stretch: {self.stretch}, "
                    f"icrq: {self.icrq}, "
                    f"nfail1: {self.nfail1}, "
                    f"nfail4: {self.nfail4}, "
                    f"psnfail: {self.psnfail}, "
                    f"keepcs: {self.keepcs}, "
                    f"delfr: {self.delfr}, "
                    f"drcpsid: {self.drcpsid}, "
                    f"drcprm: {self.drcprm}, "
                    f"intperr: {self.intperr}\n")
        else:
            return (f"control_shell name: {self.name}"
                    f"control shell id: {self.uid}, "
                    f"wrpang: {self.wrpang}, "
                    f"esort: {self.esort}, "
                    f"irnxx: {self.irnxx}, "
                    f"istupd: {self.istupd}, "
                    f"theory: {self.theory},"
                    f"bwc: {self.bwc}, "
                    f"miter: {self.miter}, "
                    f"proj: {self.proj}, "
                    f"rotascl: {self.rotascl},"
                    f"intgrd: {self.intgrd}, "
                    f"lamsht: {self.lamsht}, "
                    f"cstyp6: {self.cstyp6}, "
                    f"thshell: {self.thshell}, "
                    f"pstupd: {self.pstupd}, "
                    f"sidt4tu: {self.sidt4tu}, "
                    f"cntco: {self.cntco}, "
                    f"itsflg: {self.itsflg}, "
                    f"irquad: {self.irquad}, "
                    f"w_mode: {self.w_mode}, "
                    f"stretch: {self.stretch}, "
                    f"icrq: {self.icrq}, "
                    f"nfail1: {self.nfail1}, "
                    f"nfail4: {self.nfail4}, "
                    f"psnfail: {self.psnfail}, "
                    f"keepcs: {self.keepcs}, "
                    f"delfr: {self.delfr}, "
                    f"drcpsid: {self.drcpsid}, "
                    f"drcprm: {self.drcprm}, "
                    f"intperr: {self.intperr}\n")