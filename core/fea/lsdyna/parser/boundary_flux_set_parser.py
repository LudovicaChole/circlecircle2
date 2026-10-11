from .thermal_parser import ThermalParser


class BoundaryFluxSetParser(ThermalParser):
    keyword = '*BOUNDARY_FLUX_SET'
    names = [["ssid","pserod"],["lcid","mlc1","mlc2","mlc3","mlc4","loc","nhisv"]]
    integers = ["ssid","pserod","lcid","loc","nhisv"]
    defaults = {}
    cards = 2

