from abc import ABC, abstractmethod


class DatabaseBinaryIntfor(ABC):
    """
    user define DatabaseBinaryIntfor() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.dt = kwargs.get("dt", args[1] if len(args) > 1 else 0)
        self.lcdt = kwargs.get("lcdt", args[2] if len(args) > 2 else 0)

        self.name = kwargs.get("name", args[3] if len(args) > 3 else "default")

        if self.name == "default":
            self.name = f"database_binary_intfor_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"database_binary_intfor id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"lcdt: {self.lcdt}\n")

        else:
            return (f"database_binary_intfor name: {self.name}"
                    f"database_binary_intfor id: {self.uid}, "
                    f"dt: {self.dt}, "
                    f"lcdt: {self.lcdt}\n")