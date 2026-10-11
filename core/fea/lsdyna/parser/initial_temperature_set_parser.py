from .thermal_parser import ThermalParser


class InitialTemperatureSetParser(ThermalParser):
    keyword = '*INITIAL_TEMPERATURE_SET'
    names = [["target","temp","loc"]]
    integers = ["target","loc"]
    defaults = {}
    cards = 1

