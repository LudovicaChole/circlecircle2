from abc import ABC, abstractmethod


class ConstrainedNodalRigidBody(ABC):
    """
    user defined ConstrainedNodalRigidBody() object
    input 4 parameters:
    """
    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.pid = kwargs.get("pid", args[1] if len(args) > 1 else 0)
        self.cid = kwargs.get("cid", args[2] if len(args) > 2 else 0)
        self.sid = kwargs.get("sid", args[3] if len(args) > 3 else 0)
        self.pnode = kwargs.get("pnode", args[4] if len(args) > 4 else 0)
        self.iprt = kwargs.get("iprt", args[5] if len(args) > 5 else 0)
        self.drflag = kwargs.get("drflag", args[6] if len(args) > 6 else 0)
        self.rrflag = kwargs.get("rrflag", args[7] if len(args) > 7 else 0)

        self.name = kwargs.get("name", args[8] if len(args) > 8 else "default")

        self.nset = None

    def __repr__(self):
        if self.name == "default":
            return (f"constrained nodal rigid body id: {self.uid}, "
                    f"pid: {self.pid}, "
                    f"cid: {self.cid}, "
                    f"sid: {self.sid}, "
                    f"pnode: {self.pnode}, "
                    f"iprt: {self.iprt}, "
                    f"drflag: {self.drflag}, "
                    f"rrflag: {self.rrflag}\n")

        else:
            return (f"constrained nodal rigid body id: {self.uid}, "
                    f"pid: {self.pid}, "
                    f"cid: {self.cid}, "
                    f"sid: {self.sid}, "
                    f"pnode: {self.pnode}, "
                    f"iprt: {self.iprt}, "
                    f"drflag: {self.drflag}, "
                    f"rrflag: {self.rrflag}, "
                    f"name: {self.name}\n")
