from abc import ABC, abstractmethod


class ControlRigid(ABC):
    """
    user define ControlRigid() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.lmf = kwargs.get("lmf", args[1] if len(args) > 1 else 0)
        self.jntf = kwargs.get("jntf", args[2] if len(args) > 2 else 0)
        self.orthmd = kwargs.get("orthmd", args[3] if len(args) > 3 else 0)
        self.partm = kwargs.get("partm", args[4] if len(args) > 4 else 0)
        self.sparse = kwargs.get("sparse", args[5] if len(args) > 5 else 0)
        self.metalf = kwargs.get("metalf", args[6] if len(args) > 6 else 0)
        self.plotel = kwargs.get("plotel", args[7] if len(args) > 7 else 0)
        self.rbsms = kwargs.get("rbmsms", args[8] if len(args) > 8 else 0)

        self.name = kwargs.get("name", args[9] if len(args) > 9 else "default")

        if self.name == "default":
            self.name = f"control_rigid_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_rigid id: {self.uid}, "
                    f"lmf: {self.lmf}, "
                    f"jntf: {self.jntf}, "
                    f"orthmd: {self.orthmd}, "
                    f"partm: {self.partm}, "
                    f"sparse: {self.sparse}, "
                    f"metalf: {self.metalf}, "
                    f"plotel: {self.plotel}, "
                    f"rbsms: {self.rbsms}\n")

        else:
            return (f"control_rigid name: {self.name}, "
                    f"control_rigid id: {self.uid}, "
                    f"lmf: {self.lmf}, "
                    f"jntf: {self.jntf}, "
                    f"orthmd: {self.orthmd}, "
                    f"partm: {self.partm}, "
                    f"sparse: {self.sparse}, "
                    f"metalf: {self.metalf}, "
                    f"plotel: {self.plotel}, "
                    f"rbsms: {self.rbsms}\n")

