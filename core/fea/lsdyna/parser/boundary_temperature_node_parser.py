from .thermal_parser import ThermalParser


class BoundaryTemperatureNodeParser(ThermalParser):
    keyword = '*BOUNDARY_TEMPERATURE_NODE'
    names = [["target","tlcid","tmult","loc","tdeath","tbirth"]]
    integers = ["target","tlcid","loc"]
    defaults = {"tdeath":100000000000000000000}
    cards = 1

