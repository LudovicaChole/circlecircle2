from .thermal_parser import ThermalParser


class MatThermalIsotropicParser(ThermalParser):
    keyword = '*MAT_THERMAL_ISOTROPIC'
    names = [["tmid","tro","tgrlc","tgmult","tlat","hlat"],["hc","tc"]]
    integers = ["tmid","tgrlc"]
    defaults = {}
    cards = 2

