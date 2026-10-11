from abc import ABC, abstractmethod


class BoundaryPrescribedMotionRigid(ABC):
    """
    user define BoundaryPrescribedMotionRigid() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.typeid = kwargs.get("typeid", args[1] if len(args) > 1 else 0)
        self.dof = kwargs.get("dof", args[2] if len(args) > 2 else 0)
        self.lcid = kwargs.get("lcid", args[3] if len(args) > 3 else 0)

        self.name = kwargs.get("name", args[4] if len(args) > 4 else "default")

        if self.name == "default":
            self.name = f"boundary_prescribed_motion_rigid_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"boundary_prescribed_motion_rigid id: {self.uid}, "
                    f"typeid: {self.typeid}, "
                    f"dof: {self.dof}, "
                    f"lcid: {self.lcid}\n")

        else:
            return (f"boundary_prescribed_motion_rigid name: {self.name}"
                    f"boundary_prescribed_motion_rigid id: {self.uid}, "
                    f"typeid: {self.typeid}, "
                    f"dof: {self.dof}, "
                    f"lcid: {self.lcid}\n")
