from abc import ABC, abstractmethod


class Part(ABC):
    """
    user define Part() object
    input 4 parameters:
    Samples:

    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.pid = kwargs.get("pid", args[1] if len(args) > 1 else None)
        self.atype = kwargs.get("atype", args[2] if len(args) > 2 else None)
        self.idmat = kwargs.get("idmat", args[3] if len(args) > 3 else None)
        self.idpmat = kwargs.get("idpmat", args[4] if len(args) > 4 else None)
        self.idnumpar = kwargs.get("idnumpar", args[5] if len(args) > 5 else None)
        self.title = kwargs.get("title", args[6] if len(args) > 6 else None)
        self.dtelim = kwargs.get("dtelim", args[7] if len(args) > 7 else None)
        self.tscalf = kwargs.get("tscalf", args[8] if len(args) > 8 else None)
        self.dtratio = kwargs.get("dtratio", args[9] if len(args) > 9 else None)
        self.tcont = kwargs.get("tcont", args[10] if len(args) > 10 else None)
        self.epsini = kwargs.get("epsini", args[11] if len(args) > 11 else None)
        self.coulfric = kwargs.get("coulfric", args[12] if len(args) > 12 else None)
        self.h = kwargs.get("h", args[13] if len(args) > 13 else None)
        self.nint = kwargs.get("nint", args[14] if len(args) > 14 else None)
        self.offsetnthdo = kwargs.get("offsetnthdo", args[15] if len(args) > 15 else None)
        self.additional = kwargs.get("additional", args[16] if len(args) > 16 else None)

    def __repr__(self):
        return (f"uid: {self.uid}, "
                f"pid: {self.pid}, "
                f"atype: {self.atype}, "
                f"idmat: {self.idmat}, "
                f"idpmat: {self.idpmat}, "
                f"idnumpar: {self.idnumpar}, "
                f"title: {self.title}, "
                f"dtelim: {self.dtelim},"
                f"tscalf: {self.tscalf}, "
                f"dtratio: {self.dtratio}, "
                f"tcont: {self.tcont}, "
                f"epsini: {self.epsini}, "
                f"coulfric: {self.coulfric}, "
                f"h: {self.h}, "
                f"nint: {self.nint}, "
                f"offsetnthdo: {self.offsetnthdo}, "
                f"additional: {self.additional}\n")
