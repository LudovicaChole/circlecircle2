from abc import ABC, abstractmethod


class Node(ABC):
    """
    user define Node() object
    input 4 parameters: uid, x, y, z
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else None)
        self.x = kwargs.get("x", args[1] if len(args) > 1 else None)
        self.y = kwargs.get("y", args[2] if len(args) > 2 else None)
        self.z = kwargs.get("z", args[3] if len(args) > 3 else None)

        self.xyz = (self.x, self.y, self.z)

    def __repr__(self):
        return f"node id: {self.uid}, x: {self.x}, y: {self.y}, z: {self.z}\n"
