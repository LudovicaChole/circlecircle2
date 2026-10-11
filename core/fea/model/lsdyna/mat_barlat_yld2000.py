from abc import ABC, abstractmethod


class MatBarlatYld2000(ABC):
    """
    user define MatBarlatYld2000() object
    input 8 parameters: uid, rho, e, pr, da, db, k, name
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.rho = kwargs.get("rho", args[1] if len(args) > 1 else 0)
        self.e = kwargs.get("e", args[2] if len(args) > 2 else 0)
        self.pr = kwargs.get("pr", args[3] if len(args) > 3 else 0)
        self.fit = kwargs.get("fit", args[4] if len(args) > 4 else 0)
        self.beta = kwargs.get("beta", args[5] if len(args) > 5 else 0)
        self.iter = kwargs.get("iter", args[6] if len(args) > 6 else 0)
        self.iscale = kwargs.get("iscale", args[7] if len(args) > 7 else 0)
        self.k = kwargs.get("k", args[8] if len(args) > 8 else 0)
        self.e0 = kwargs.get("e0", args[9] if len(args) > 9 else 0)
        self.n = kwargs.get("n", args[10] if len(args) > 10 else 0)
        self.c = kwargs.get("c", args[11] if len(args) > 11 else 0)
        self.p = kwargs.get("p", args[12] if len(args) > 12 else 0)
        self.hard = kwargs.get("hard", args[13] if len(args) > 13 else 0)
        self.lcss = self.hard
        self.a = kwargs.get("a", args[14] if len(args) > 14 else 0)
        self.alpha1 = kwargs.get("alpha1", args[15] if len(args) > 15 else 0)
        self.alpha2 = kwargs.get("alpha2", args[16] if len(args) > 16 else 0)
        self.alpha3 = kwargs.get("alpha3", args[17] if len(args) > 17 else 0)
        self.alpha4 = kwargs.get("alpha4", args[18] if len(args) > 18 else 0)
        self.alpha5 = kwargs.get("alpha5", args[19] if len(args) > 19 else 0)
        self.alpha6 = kwargs.get("alpha6", args[20] if len(args) > 20 else 0)
        self.alpha7 = kwargs.get("alpha7", args[21] if len(args) > 21 else 0)
        self.alpha8 = kwargs.get("alpha8", args[22] if len(args) > 22 else 0)
        self.aopt = kwargs.get("aopt", args[23] if len(args) > 23 else 0)
        self.offang = kwargs.get("offang", args[24] if len(args) > 24 else 0)
        self.p4 = kwargs.get("p4", args[25] if len(args) > 25 else 0)
        self.htflag = kwargs.get("htflag", args[26] if len(args) > 26 else 0)
        self.hta = kwargs.get("hta", args[27] if len(args) > 27 else 0)
        self.htb = kwargs.get("htb", args[28] if len(args) > 28 else 0)
        self.htc = kwargs.get("htc", args[29] if len(args) > 29 else 0)
        self.htd = kwargs.get("htd", args[30] if len(args) > 30 else 0)
        self.a1 = kwargs.get("a1", args[31] if len(args) > 31 else 0)
        self.a2 = kwargs.get("a2", args[32] if len(args) > 32 else 0)
        self.a3 = kwargs.get("a3", args[33] if len(args) > 33 else 0)
        self.v1 = kwargs.get("v1", args[34] if len(args) > 34 else 0)
        self.v2 = kwargs.get("v2", args[35] if len(args) > 35 else 0)
        self.v3 = kwargs.get("v3", args[36] if len(args) > 36 else 0)
        self.d1 = kwargs.get("d1", args[37] if len(args) > 37 else 0)
        self.d2 = kwargs.get("d2", args[38] if len(args) > 38 else 0)
        self.d3 = kwargs.get("d3", args[39] if len(args) > 39 else 0)
        self.usrfail = kwargs.get("usrfail", args[40] if len(args) > 40 else 0)

        self.name = kwargs.get("name", args[41] if len(args) > 41 else "default")

        self.tag = "plastic"

        self.map_tag = None

        if self.name == "default":
            self.name = f"mat_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"mat barlat yld2000 id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"fit: {self.fit}, "
                    f"beta: {self.beta}, "
                    f"iter: {self.iter}, "
                    f"iscale: {self.iscale}, "
                    f"k: {self.k}, "
                    f"e0: {self.e0}, "
                    f"n: {self.n}, "
                    f"c, {self.c}, "
                    f"p, {self.p}, "
                    f"hard, {self.hard}, "
                    f"a, {self.a}, "
                    f"alpha1: {self.alpha1}, "
                    f"alpha2: {self.alpha2}, "
                    f"alpha3: {self.alpha3}, "
                    f"alpha4: {self.alpha4}, "
                    f"alpha5: {self.alpha5}, "
                    f"alpha6: {self.alpha6}, "
                    f"alpha7: {self.alpha7}, "
                    f"alpha8: {self.alpha8}, "
                    f"aopt: {self.aopt}, "
                    f"offang: {self.offang}, "
                    f"p4: {self.p4}, "
                    f"htflag: {self.htflag}, "
                    f"hta: {self.hta}, "
                    f"htb: {self.htb}, "
                    f"htc: {self.htc}, "
                    f"htd: {self.htd}, "
                    f"a1: {self.a1}, "
                    f"a2: {self.a2}, "
                    f"a3: {self.a3}, "
                    f"v1: {self.v1}, "
                    f"v2: {self.v2}, "
                    f"v3: {self.v3}, "
                    f"d1: {self.d1}, "
                    f"d2: {self.d2}, "
                    f"d3: {self.d3}, "
                    f"usrfail: {self.usrfail}\n")

        else:
            return (f"mat barlat yld2000 id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"fit: {self.fit}, "
                    f"beta: {self.beta}, "
                    f"iter: {self.iter}, "
                    f"iscale: {self.iscale}, "
                    f"k: {self.k}, "
                    f"e0: {self.e0}, "
                    f"n: {self.n}, "
                    f"c, {self.c}, "
                    f"p, {self.p}, "
                    f"hard, {self.hard}, "
                    f"a, {self.a}, "
                    f"alpha1: {self.alpha1}, "
                    f"alpha2: {self.alpha2}, "
                    f"alpha3: {self.alpha3}, "
                    f"alpha4: {self.alpha4}, "
                    f"alpha5: {self.alpha5}, "
                    f"alpha6: {self.alpha6}, "
                    f"alpha7: {self.alpha7}, "
                    f"alpha8: {self.alpha8}, "
                    f"aopt: {self.aopt}, "
                    f"offang: {self.offang}, "
                    f"p4: {self.p4}, "
                    f"htflag: {self.htflag}, "
                    f"hta: {self.hta}, "
                    f"htb: {self.htb}, "
                    f"htc: {self.htc}, "
                    f"htd: {self.htd}, "
                    f"a1: {self.a1}, "
                    f"a2: {self.a2}, "
                    f"a3: {self.a3}, "
                    f"v1: {self.v1}, "
                    f"v2: {self.v2}, "
                    f"v3: {self.v3}, "
                    f"d1: {self.d1}, "
                    f"d2: {self.d2}, "
                    f"d3: {self.d3}, "
                    f"usrfail: {self.usrfail}, "
                    f"name: {self.name}\n")