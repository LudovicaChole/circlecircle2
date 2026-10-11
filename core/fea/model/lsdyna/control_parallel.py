from abc import ABC, abstractmethod


class ControlParallel(ABC):
    """
    user define ControlParallel() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.ncpu = kwargs.get("ncpu", args[1] if len(args) > 1 else 0)
        self.numrhs = kwargs.get("numrhs", args[2] if len(args) > 2 else 0)
        self.const = kwargs.get("const", args[3] if len(args) > 3 else 0)
        self.para = kwargs.get("para", args[4] if len(args) > 4 else 0)

        self.name = kwargs.get("name", args[5] if len(args) > 5 else "default")

        if self.name == "default":
            self.name = f"control_parallel_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_parallel id: {self.uid}, "
                    f"ncpu: {self.ncpu}, "
                    f"numrhs: {self.numrhs}, "
                    f"const: {self.const}, "
                    f"para: {self.para}\n")

        else:
            return (f"control_parallel name: {self.name}, "
                    f"control_parallel id: {self.uid}, "
                    f"ncpu: {self.ncpu}, "
                    f"numrhs: {self.numrhs}, "
                    f"const: {self.const}, "
                    f"para: {self.para}\n")
