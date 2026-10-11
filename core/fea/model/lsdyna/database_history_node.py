from abc import ABC, abstractmethod


class DatabaseHistoryNode(ABC):
    """
    user define DatabaseHistoryNode() object
    input 3 parameters: uid, name, ids
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.name = kwargs.get("name", args[1] if len(args) > 1 else "default")

        self.ids = []

    def __repr__(self):
        if self.name == "default":
            return (f"database_history_node id: {self.uid}, "
                    f"include ids: {self.ids}\n")
        else:
            return (f"database_history_node id: {self.uid}, "
                    f"name: {self.name}, "
                    f"include ids: {self.ids}\n")
