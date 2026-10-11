from .fluid_parser import FluidParser


class IcfdSectionParser(FluidParser):
    keyword = '*ICFD_SECTION'
    rows = [["sid"]]
    integers = ["sid"]
    repeat = True
    widths = (10,) * 8

