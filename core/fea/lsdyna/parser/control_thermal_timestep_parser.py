from .thermal_parser import ThermalParser


class ControlThermalTimestepParser(ThermalParser):
    keyword = '*CONTROL_THERMAL_TIMESTEP'
    names = [["ts","tip","its","tmin","tmax","dtemp","tscp","lcts"]]
    integers = ["ts","lcts"]
    defaults = {"tip":1,"dtemp":1,"tscp":0.5}
    cards = 1

