from .fluid_parser import FluidParser


class IcfdPartVolParser(FluidParser):
    keyword = '*ICFD_PART_VOL'
    rows = [["pid","secid","mid"],["spid1","spid2","spid3","spid4","spid5","spid6","spid7","spid8"]]
    integers = ["pid","secid","mid","spid1","spid2","spid3","spid4","spid5","spid6","spid7","spid8"]
    repeat = True
    widths = (10,) * 8

