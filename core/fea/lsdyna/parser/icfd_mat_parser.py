from .fluid_parser import FluidParser


class IcfdMatParser(FluidParser):
    keyword = '*ICFD_MAT'
    rows = [["mid","flg","ro","vis","st","stsf","ca"],["hc","tc","beta","prt","hcsflcid","tcsflcid"],["nnmoid","pmmoid"]]
    integers = ["mid","flg","stsf","hcsflcid","tcsflcid","nnmoid","pmmoid"]
    repeat = False
    widths = (10,) * 8

