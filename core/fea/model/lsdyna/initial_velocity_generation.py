from abc import ABC, abstractmethod


class InitialVelocityGeneration(ABC):
    """
    user define InitialVelocityGeneration() object
    input 4 parameters: uid, x, y, z
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.pid = kwargs.get("pid", args[1] if len(args) > 1 else 0)
        self.styp = kwargs.get("styp", args[2] if len(args) > 2 else 0)
        self.omega = kwargs.get("omega", args[3] if len(args) > 3 else 0)
        self.vx = kwargs.get("vx", args[4] if len(args) > 4 else 0)
        self.vy = kwargs.get("vy", args[5] if len(args) > 5 else 0)
        self.vz = kwargs.get("vz", args[6] if len(args) > 6 else 0)
        self.ivant = kwargs.get("ivant", args[7] if len(args) > 7 else 0)
        self.lcid = kwargs.get("lcid", args[8] if len(args) > 8 else 0)
        self.xc = kwargs.get("xc", args[9] if len(args) > 9 else 0)
        self.yc = kwargs.get("yc", args[10] if len(args) > 10 else 0)
        self.zc = kwargs.get("zc", args[11] if len(args) > 11 else 0)
        self.nx = kwargs.get("nx", args[12] if len(args) > 12 else 0)
        self.ny = kwargs.get("ny", args[13] if len(args) > 13 else 0)
        self.nz = kwargs.get("nz", args[14] if len(args) > 14 else 0)
        self.phase = kwargs.get("phase", args[15] if len(args) > 15 else 0)
        self.irigid = kwargs.get("irigid", args[16] if len(args) > 16 else 0)

        self.name = kwargs.get("name", args[17] if len(args) > 17 else "default")

        if self.name == "default":
            self.name = f"initial_velocity_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"initial velocity generation id: {self.uid}, "
                    f"pid: {self.pid}, "
                    f"styp: {self.styp}, "
                    f"omega: {self.omega}, "
                    f"vx: {self.vx}, "
                    f"vy: {self.vy}, "
                    f"vz: {self.vz}, "
                    f"ivant: {self.ivant}, "
                    f"lcid: {self.lcid}, "
                    f"xc: {self.xc}, "
                    f"yc: {self.yc}, "
                    f"zc: {self.zc}, "
                    f"nx: {self.nx}, "
                    f"ny: {self.ny}, "
                    f"nz: {self.nz}, "
                    f"phase: {self.phase}, "
                    f"irigid: {self.irigid}\n")

        else:
            return (f"initial velocity generation id: {self.uid}, "
                    f"pid: {self.pid}, "
                    f"styp: {self.styp}, "
                    f"omega: {self.omega}, "
                    f"vx: {self.vx}, "
                    f"vy: {self.vy}, "
                    f"vz: {self.vz}, "
                    f"ivant: {self.ivant}, "
                    f"lcid: {self.lcid}, "
                    f"xc: {self.xc}, "
                    f"yc: {self.yc}, "
                    f"zc: {self.zc}, "
                    f"nx: {self.nx}, "
                    f"ny: {self.ny}, "
                    f"nz: {self.nz}, "
                    f"phase: {self.phase}, "
                    f"irigid: {self.irigid}, "
                    f"name: {self.name}\n")
