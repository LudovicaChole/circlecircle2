from abc import ABC, abstractmethod


class ControlBulkViscosity(ABC):
    """
    user define ControlBulkViscosity() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.q1 = kwargs.get("q1", args[1] if len(args) > 1 else 0)
        self.q2 = kwargs.get("q2", args[2] if len(args) > 2 else 0)
        self.type_c = kwargs.get("type_c", args[3] if len(args) > 3 else 0)
        self.btype = kwargs.get("btype", args[4] if len(args) > 4 else 0)

        self.name = kwargs.get("name", args[5] if len(args) > 5 else "default")

        if self.name == "default":
            self.name = f"control_bulk_viscosity_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_bulk_viscosity id: {self.uid}, "
                    f"q1: {self.q1}, "
                    f"q2: {self.q2}, "
                    f"type: {self.type_c}, "
                    f"btype: {self.btype}\n")

        else:
            return (f"control_dynamic_relaxation name: {self.name}, "
                    f"control_bulk_viscosity id: {self.uid}, "
                    f"q1: {self.q1}, "
                    f"q2: {self.q2}, "
                    f"type: {self.type_c}, "
                    f"btype: {self.btype}\n")
