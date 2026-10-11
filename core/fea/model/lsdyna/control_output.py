from abc import ABC, abstractmethod


class ControlOutput(ABC):
    """
    user define ControlOutput() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.npopt = kwargs.get("npopt", args[1] if len(args) > 1 else 0)
        self.neecho = kwargs.get("neecho", args[2] if len(args) > 2 else 0)
        self.nrefup = kwargs.get("nrefup", args[3] if len(args) > 3 else 0)
        self.iaccop = kwargs.get("iaccop", args[4] if len(args) > 4 else 0)
        self.opifs = kwargs.get("opifs", args[5] if len(args) > 5 else 0)
        self.ipnint = kwargs.get("ipnint", args[6] if len(args) > 6 else 0)
        self.ikedit = kwargs.get("ikedit", args[7] if len(args) > 7 else 0)
        self.iflush = kwargs.get("iflush", args[8] if len(args) > 8 else 0)
        self.iprtf = kwargs.get("iprtf", args[9] if len(args) > 9 else 0)
        self.ierode = kwargs.get("ierode", args[10] if len(args) > 10 else 0)
        self.tet10s8 = kwargs.get("tet10s8", args[11] if len(args) > 11 else 0)
        self.msgmax = kwargs.get("msgmax", args[12] if len(args) > 12 else 0)
        self.ipcurv = kwargs.get("ipcurv", args[13] if len(args) > 13 else 0)
        self.gmdt = kwargs.get("gmdt", args[14] if len(args) > 14 else 0)
        self.ip1dblt = kwargs.get("ip1dblt", args[15] if len(args) > 15 else 0)
        self.eocs = kwargs.get("eocs", args[16] if len(args) > 16 else 0)

        self.name = kwargs.get("name", args[17] if len(args) > 17 else "default")

        if self.name == "default":
            self.name = f"control_output_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_output id: {self.uid}, "
                    f"npopt: {self.npopt}, "
                    f"neecho: {self.neecho}, "
                    f"nrefup: {self.nrefup}, "
                    f"iaccop: {self.iaccop}, "
                    f"opifs: {self.opifs}, "
                    f"ipnint: {self.ipnint}, "
                    f"ikedit: {self.ikedit}, "
                    f"iflush: {self.iflush}, "
                    f"iprtf: {self.iprtf}, "
                    f"ierode: {self.ierode}, "
                    f"tet10s8: {self.tet10s8}, "
                    f"msgmax: {self.msgmax}, "
                    f"ipcurv: {self.ipcurv}, "
                    f"gmdt: {self.gmdt}, "
                    f"ip1dblt: {self.ip1dblt}, "
                    f"eocs: {self.eocs}\n")

        else:
            return (f"control_parallel name: {self.name}, "
                    f"control_output id: {self.uid}, "
                    f"npopt: {self.npopt}, "
                    f"neecho: {self.neecho}, "
                    f"nrefup: {self.nrefup}, "
                    f"iaccop: {self.iaccop}, "
                    f"opifs: {self.opifs}, "
                    f"ipnint: {self.ipnint}, "
                    f"ikedit: {self.ikedit}, "
                    f"iflush: {self.iflush}, "
                    f"iprtf: {self.iprtf}, "
                    f"ierode: {self.ierode}, "
                    f"tet10s8: {self.tet10s8}, "
                    f"msgmax: {self.msgmax}, "
                    f"ipcurv: {self.ipcurv}, "
                    f"gmdt: {self.gmdt}, "
                    f"ip1dblt: {self.ip1dblt}, "
                    f"eocs: {self.eocs}\n")