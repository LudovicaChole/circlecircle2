from abc import ABC, abstractmethod


class MatElastic(ABC):
    """
    user define MatElastic() object
    input 8 parameters: uid, rho, e, pr, da, db, k, name
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.rho = kwargs.get("rho", args[1] if len(args) > 1 else 0)
        self.e = kwargs.get("e", args[2] if len(args) > 2 else 0)
        self.pr = kwargs.get("pr", args[3] if len(args) > 3 else 0)
        self.da = kwargs.get("da", args[4] if len(args) > 4 else 0)
        self.db = kwargs.get("db", args[5] if len(args) > 5 else 0)
        self.k = kwargs.get("k", args[6] if len(args) > 6 else 0)

        self.name = kwargs.get("name", args[7] if len(args) > 7 else "default")

        self.tag = "elastic"

        self.map_tag = None

        if self.name == "default":
            self.name = f"mat_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"mat elastic id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"da: {self.da}, "
                    f"db: {self.db}, "
                    f"k: {self.k}\n")

        else:
            return (f"mat elastic id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"da: {self.da}, "
                    f"db: {self.db}, "
                    f"k: {self.k}, "
                    f"name: {self.name}\n")
