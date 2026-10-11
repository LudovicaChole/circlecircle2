from abc import ABC, abstractmethod


class MatPiecewiseLinearPlasticityLogInterpolation(ABC):
    """
    user define MatPiecewiseLinearPlasticityLogInterpolation() object
    input 8 parameters: uid, rho, e, pr, da, db, k, name
    """

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", args[0] if len(args) > 0 else 0)
        self.rho = kwargs.get("rho", args[1] if len(args) > 1 else 0)
        self.e = kwargs.get("e", args[2] if len(args) > 2 else 0)
        self.pr = kwargs.get("pr", args[3] if len(args) > 3 else 0)
        self.sigy = kwargs.get("sigy", args[4] if len(args) > 4 else 0)
        self.etan = kwargs.get("etan", args[5] if len(args) > 5 else 0)
        self.fail = kwargs.get("fail", args[6] if len(args) > 6 else 0)
        self.tdel = kwargs.get("tdel", args[7] if len(args) > 7 else 0)
        self.c = kwargs.get("c", args[8] if len(args) > 8 else 0)
        self.p = kwargs.get("p", args[9] if len(args) > 9 else 0)
        self.lcss = kwargs.get("lcss", args[10] if len(args) > 10 else 0)
        self.lcsr = kwargs.get("lcsr", args[11] if len(args) > 11 else 0)
        self.vp = kwargs.get("vp", args[12] if len(args) > 12 else 0)
        self.lcf = kwargs.get("lcf", args[13] if len(args) > 13 else 0)
        self.eps1 = kwargs.get("eps1", args[14] if len(args) > 14 else 0)
        self.eps2 = kwargs.get("eps2", args[15] if len(args) > 15 else 0)
        self.eps3 = kwargs.get("eps3", args[16] if len(args) > 16 else 0)
        self.eps4 = kwargs.get("eps4", args[17] if len(args) > 17 else 0)
        self.eps5 = kwargs.get("eps5", args[18] if len(args) > 18 else 0)
        self.eps6 = kwargs.get("eps6", args[19] if len(args) > 19 else 0)
        self.eps7 = kwargs.get("eps7", args[20] if len(args) > 20 else 0)
        self.eps8 = kwargs.get("eps8", args[21] if len(args) > 21 else 0)
        self.es1 = kwargs.get("es1", args[22] if len(args) > 22 else 0)
        self.es2 = kwargs.get("es2", args[23] if len(args) > 23 else 0)
        self.es3 = kwargs.get("es3", args[24] if len(args) > 24 else 0)
        self.es4 = kwargs.get("es4", args[25] if len(args) > 25 else 0)
        self.es5 = kwargs.get("es5", args[26] if len(args) > 26 else 0)
        self.es6 = kwargs.get("es6", args[27] if len(args) > 27 else 0)
        self.es7 = kwargs.get("es7", args[28] if len(args) > 28 else 0)
        self.es8 = kwargs.get("es8", args[29] if len(args) > 29 else 0)

        self.name = kwargs.get("name", args[30] if len(args) > 30 else "default")

        self.tag = "plastic"

        self.map_tag = None

        if self.name == "default":
            self.name = f"mat_{self.uid}"

    def __repr__(self):
        if self.name == "default":
            return (f"mat piecewise linear plasticity log interpolation id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"sigy: {self.sigy}, "
                    f"etan: {self.etan}, "
                    f"fail: {self.fail}, "
                    f"tdel: {self.tdel}, "
                    f"c: {self.c}, "
                    f"p: {self.p}, "
                    f"lcss: {self.lcss}, "
                    f"lcsr: {self.lcsr}, "
                    f"vp: {self.vp}, "
                    f"lcf: {self.lcf}, "
                    f"eps1: {self.eps1}, "
                    f"eps2: {self.eps2}, "
                    f"eps3: {self.eps3}, "
                    f"eps4: {self.eps4}, "
                    f"eps5: {self.eps5}, "
                    f"eps6: {self.eps6}, "
                    f"eps7: {self.eps7}, "
                    f"eps8: {self.eps8}, "
                    f"es1: {self.es1}, "
                    f"es2: {self.es2}, "
                    f"es3: {self.es3}, "
                    f"es4: {self.es4}, "
                    f"es5: {self.es5}, "
                    f"es6: {self.es6}, "
                    f"es7: {self.es7}, "
                    f"es8: {self.es8}\n")

        else:
            return (f"mat piecewise linear plasticity log interpolation id: {self.uid}, "
                    f"rho: {self.rho}, "
                    f"e: {self.e}, "
                    f"pr: {self.pr}, "
                    f"sigy: {self.sigy}, "
                    f"etan: {self.etan}, "
                    f"fail: {self.fail}, "
                    f"tdel: {self.tdel}, "
                    f"c: {self.c}, "
                    f"p: {self.p}, "
                    f"lcss: {self.lcss}, "
                    f"lcsr: {self.lcsr}, "
                    f"vp: {self.vp}, "
                    f"lcf: {self.lcf}, "
                    f"eps1: {self.eps1}, "
                    f"eps2: {self.eps2}, "
                    f"eps3: {self.eps3}, "
                    f"eps4: {self.eps4}, "
                    f"eps5: {self.eps5}, "
                    f"eps6: {self.eps6}, "
                    f"eps7: {self.eps7}, "
                    f"eps8: {self.eps8}, "
                    f"es1: {self.es1}, "
                    f"es2: {self.es2}, "
                    f"es3: {self.es3}, "
                    f"es4: {self.es4}, "
                    f"es5: {self.es5}, "
                    f"es6: {self.es6}, "
                    f"es7: {self.es7}, "
                    f"es8: {self.es8}, "
                    f"name: {self.name}\n")
