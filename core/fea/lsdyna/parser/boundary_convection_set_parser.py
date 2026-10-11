from .thermal_parser import ThermalParser


class BoundaryConvectionSetParser(ThermalParser):
    keyword = '*BOUNDARY_CONVECTION_SET'
    names = (('ssid', 'pserod'), ('hlcid', 'hmult', 'tlcid', 'tmult', 'loc'))
    integers = ('ssid', 'pserod', 'hlcid', 'tlcid', 'loc')
    cards = 2
