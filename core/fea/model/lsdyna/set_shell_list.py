from abc import ABC, abstractmethod


class SetShellList(ABC):
    """
    user define SetShellList() object
    input 6 parameters: uid, da1, da2, da3, da4, solver
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.da1 = kwargs.get("da1", args[1] if len(args) > 1 else 0)
        self.da2 = kwargs.get("da2", args[2] if len(args) > 2 else 0)
        self.da3 = kwargs.get("da3", args[3] if len(args) > 3 else 0)
        self.da4 = kwargs.get("da4", args[4] if len(args) > 4 else 0)
        self.solver = kwargs.get("solver", args[5] if len(args) > 5 else None)

        self.name = kwargs.get("name", args[6] if len(args) > 6 else "default")

        self.ids = []

    def __repr__(self):
        if self.name == "default":
            return (f"set_shell_list id: {self.uid}, "
                    f"da1: {self.da1}, "
                    f"da2: {self.da2}, "
                    f"da3: {self.da3}, "
                    f"da4: {self.da4}, "
                    f"solver: {self.solver}, "
                    f"include ids: {self.ids}\n")

        else:
            return (f"set_shell_list id: {self.uid}, "
                    f"da1: {self.da1}, "
                    f"da2: {self.da2}, "
                    f"da3: {self.da3}, "
                    f"da4: {self.da4}, "
                    f"solver: {self.solver}, "
                    f"name: {self.name}, "
                    f"include ids: {self.ids}\n")
