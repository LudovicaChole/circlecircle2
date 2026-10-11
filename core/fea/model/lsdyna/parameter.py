from abc import ABC, abstractmethod


class Parameter(ABC):
    """
    user define Parameter() object
    input 3 parameters: type, name, value
    """

    def __init__(self, *args, **kwargs):
        self.type = kwargs.get("type", args[0] if len(args) > 0 else None)
        self.name = kwargs.get("name", args[1] if len(args) > 1 else None)
        self.value = kwargs.get("value", args[2] if len(args) > 2 else None)

    def __repr__(self):
        return (f"parameter type: {self.type}, "
                f"name: {self.name}, "
                f"value: {self.value}\n")
