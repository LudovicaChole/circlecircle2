from abc import ABC, abstractmethod


class MatRigid(ABC):
    """
    user define MatElastic() object
    input 8 parameters: uid, rho, e, pr, da, db, k, name
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.rho = kwargs.get("rho", args[1] if len(args) > 1 else 0)
        self.e = kwargs.get("e", args[2] if len(args) > 2 else 0)
        self.pr = kwargs.get("pr", args[3] if len(args) > 3 else 0)
        self.n = kwargs.get("n", args[4] if len(args) > 4 else 0)
        self.couple = kwargs.get("couple", args[5] if len(args) > 5 else 0)
        self.m = kwargs.get("m", args[6] if len(args) > 6 else 0)
        self.alias = kwargs.get("alias", args[7] if len(args) > 7 else 0)
        self.cmo = kwargs.get("cmo", args[8] if len(args) > 8 else 0)
        self.con1 = kwargs.get("con1", args[9] if len(args) > 9 else 0)
        self.con2 = kwargs.get("con2", args[10] if len(args) > 10 else 0)
        self.a1 = kwargs.get("a1", args[11] if len(args) > 11 else 0)
        self.a2 = kwargs.get("a2", args[12] if len(args) > 12 else 0)
        self.a3 = kwargs.get("a3", args[13] if len(args) > 13 else 0)
        self.v1 = kwargs.get("v1", args[14] if len(args) > 14 else 0)
        self.v2 = kwargs.get("v2", args[15] if len(args) > 15 else 0)
        self.v3 = kwargs.get("v3", args[16] if len(args) > 16 else 0)

        self.name = kwargs.get("name", args[17] if len(args) > 17 else "default")

        self.tag = "rigid"

        self.map_tag = None

        if self.name == "default":
            self.name = f"mat_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"mat rigid id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"n: {self.n}, "
                    f"couple: {self.couple}, "
                    f"m: {self.m}, "
                    f"alias: {self.alias}, "
                    f"cmo: {self.cmo}, "
                    f"con1: {self.con1}, "
                    f"con2: {self.con2}, "
                    f"a1: {self.a1}, "
                    f"a2: {self.a2}, "
                    f"a3: {self.a3}, "
                    f"v1: {self.v1}, "
                    f"v2: {self.v2}, "
                    f"v3: {self.v3}\n")

        else:
            return (f"mat rigid id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"n: {self.n}, "
                    f"couple: {self.couple}, "
                    f"m: {self.m}, "
                    f"alias: {self.alias}, "
                    f"cmo: {self.cmo}, "
                    f"con1: {self.con1}, "
                    f"con2: {self.con2}, "
                    f"a1: {self.a1}, "
                    f"a2: {self.a2}, "
                    f"a3: {self.a3}, "
                    f"v1: {self.v1}, "
                    f"v2: {self.v2}, "
                    f"v3: {self.v3}, "
                    f"name: {self.name}\n")
