from .fluid_parser import FluidParser


class IcfdControlTimeParser(FluidParser):
    keyword = '*ICFD_CONTROL_TIME'
    rows = [["ttm","dt","cfl","lcidsf","dtmin","dtmax","dtinit","tdeath"],["dtt"],["btbl"]]
    integers = ["lcidsf","btbl"]
    repeat = False
    widths = (10,) * 8

