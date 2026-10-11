from .thermal_parser import ThermalParser


class ControlThermalSolverParser(ThermalParser):
    keyword = '*CONTROL_THERMAL_SOLVER'
    names = [["atype","ptype","solver","-","gpt","eqheat","fwork","sbc"]]
    integers = ["atype","ptype","solver","gpt"]
    defaults = {}
    cards = 1

