from .fluid_parser import FluidParser


class IcfdPartParser(FluidParser):
    keyword = '*ICFD_PART'
    rows = [["pid","secid","mid"]]
    integers = ["pid","secid","mid"]
    repeat = True
    widths = (10,) * 8

