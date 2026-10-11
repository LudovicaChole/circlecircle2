from abc import ABC, abstractmethod


class Title(ABC):
    """
    user define Title() object
    input 1 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.context = kwargs.get("context", args[1] if len(args) > 1 else 0)

        self.name = kwargs.get("name", args[2] if len(args) > 2 else "default")

        if self.name == "default":
            self.name = f"title_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"title id: {self.uid}, "
                    f"context: {self.context}\n")

        else:
            return (f"title name: {self.name}, "
                    f"title id: {self.uid}, "
                    f"context: {self.context} \n")