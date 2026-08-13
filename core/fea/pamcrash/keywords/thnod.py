from abc import ABC, abstractmethod


class ThNod(ABC):
    """
    user define ThNod() object
    input 4 parameters:
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.title = kwargs.get("title", args[1] if len(args) > 1 else None)
        self.entity_selection = kwargs.get("entity_selection", args[2] if len(args) > 2 else None)

    def __repr__(self):
        return f"thnod id: {self.uid}, title: {self.title}, entity_selection: {self.entity_selection}\n"
