from .thermal_parser import ThermalParser


class InitialTemperatureNodeParser(ThermalParser):
    keyword = '*INITIAL_TEMPERATURE_NODE'
    names = [["target","temp","loc"]]
    integers = ["target","loc"]
    defaults = {}
    cards = 1

