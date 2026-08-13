from abc import ABC, abstractmethod


class Node(ABC):
    """
    user define Node() object
    input 4 parameters: uid, x, y, z
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.nid = kwargs.get("nid", args[1] if len(args) > 1 else None)
        self.x = kwargs.get("x", args[2] if len(args) > 2 else None)
        self.y = kwargs.get("y", args[3] if len(args) > 3 else None)
        self.z = kwargs.get("z", args[4] if len(args) > 4 else None)

    def __repr__(self):
        return (f"node uid: {self.uid}, "
                f"nid: {self.nid}, "
                f"x: {self.x}, "
                f"y: {self.y}, "
                f"z: {self.z}\n")
