from abc import ABC, abstractmethod


class End(ABC):
    """
    user define KeyWord() object
    input 0 parameters
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)

    def __repr__(self):
        return f"end has no properties\n"
