from .boundary_convection_set_parser import BoundaryConvectionSetParser


class BoundaryConvectionSegmentParser(BoundaryConvectionSetParser):
    keyword = '*BOUNDARY_CONVECTION_SEGMENT'
    names = (('n1', 'n2', 'n3', 'n4'), ('hlcid', 'hmult', 'tlcid', 'tmult', 'loc'))
    integers = ('n1', 'n2', 'n3', 'n4', 'hlcid', 'tlcid', 'loc')
