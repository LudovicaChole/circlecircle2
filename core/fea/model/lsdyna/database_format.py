from abc import ABC, abstractmethod


class DatabaseFormat(ABC):
    """
    user define DatabaseFormat() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.iform = kwargs.get("dt", args[1] if len(args) > 1 else 0)
        self.ibinary = kwargs.get("binary", args[2] if len(args) > 2 else 0)

        self.name = kwargs.get("name", args[3] if len(args) > 3 else "default")

        if self.name == "default":
            self.name = f"database_format_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"database_format id: {self.uid}, "
                    f"iform: {self.iform}, "
                    f"ibinary: {self.ibinary}\n")

        else:
            return (f"database_format name: {self.name}"
                    f"database_format id: {self.uid}, "
                    f"iform: {self.iform}, "
                    f"ibinary: {self.ibinary}\n")