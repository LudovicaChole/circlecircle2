from abc import ABC, abstractmethod


class KeyWord(ABC):
    """
    user define KeyWord() object
    input 0 parameters
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)

    def __repr__(self):
        return f"keyword has no properties\n"
