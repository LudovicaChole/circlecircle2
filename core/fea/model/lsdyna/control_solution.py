from abc import ABC, abstractmethod


class ControlSolution(ABC):
    """
    user define ControlSolution() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.soln = kwargs.get("soln", args[1] if len(args) > 1 else 0)
        self.nlq = kwargs.get("nlq", args[2] if len(args) > 2 else 0)
        self.isnan = kwargs.get("isnan", args[3] if len(args) > 3 else 0)
        self.lcint = kwargs.get("lcint", args[4] if len(args) > 4 else 0)
        self.lcacc = kwargs.get("lcacc", args[5] if len(args) > 5 else 0)
        self.ncdcf = kwargs.get("ncdcf", args[6] if len(args) > 6 else 0)

        self.name = kwargs.get("name", args[7] if len(args) > 7 else "default")

        if self.name == "default":
            self.name = f"control_solution_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_solution id: {self.uid}, "
                    f"soln: {self.soln}, "
                    f"nlq: {self.nlq}, "
                    f"isnan: {self.isnan}, "
                    f"lcint: {self.lcint}, "
                    f"lcacc: {self.lcacc}, "
                    f"ncdcf: {self.ncdcf}\n")

        else:
            return (f"control_solution name: {self.name}"
                    f"control_solution id: {self.uid}, "
                    f"soln: {self.soln}, "
                    f"nlq: {self.nlq}, "
                    f"isnan: {self.isnan}, "
                    f"lcint: {self.lcint}, "
                    f"lcacc: {self.lcacc}, "
                    f"ncdcf: {self.ncdcf}\n")