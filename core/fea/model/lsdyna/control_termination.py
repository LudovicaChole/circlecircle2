from abc import ABC, abstractmethod


class ControlTermination(ABC):
    """
    user define ControlTermination() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.endtim = kwargs.get("endtim", args[1] if len(args) > 1 else 0)
        self.endcyc = kwargs.get("endcyc", args[2] if len(args) > 2 else 0)
        self.dtmin = kwargs.get("dtmin", args[3] if len(args) > 3 else 0)
        self.endeng = kwargs.get("endeng", args[4] if len(args) > 4 else 0)
        self.endmas = kwargs.get("endmas", args[5] if len(args) > 5 else 0)
        self.nosol = kwargs.get("nosol", args[6] if len(args) > 6 else 0)

        self.name = kwargs.get("name", args[7] if len(args) > 7 else "default")

        if self.name == "default":
            self.name = f"control_termination_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"control_termination id: {self.uid}, "
                    f"endtim: {self.endtim}, "
                    f"endcyc: {self.endcyc}, "
                    f"dtmin: {self.dtmin}, "
                    f"endeng: {self.endeng}, "
                    f"endmas: {self.endmas}, "
                    f"nosol: {self.nosol}\n")

        else:
            return (f"control_termination name: {self.name}, "
                    f"control_termination id: {self.uid}, "
                    f"endtim: {self.endtim}, "
                    f"endcyc: {self.endcyc}, "
                    f"dtmin: {self.dtmin}, "
                    f"endeng: {self.endeng}, "
                    f"endmas: {self.endmas}, "
                    f"nosol: {self.nosol}\n")

