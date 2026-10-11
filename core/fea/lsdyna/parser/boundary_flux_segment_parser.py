from .thermal_parser import ThermalParser


class BoundaryFluxSegmentParser(ThermalParser):
    keyword = '*BOUNDARY_FLUX_SEGMENT'
    names = [["n1","n2","n3","n4"],["lcid","mlc1","mlc2","mlc3","mlc4","loc","nhisv"]]
    integers = ["n1","n2","n3","n4","lcid","loc","nhisv"]
    defaults = {}
    cards = 2

