from .fluid_parser import FluidParser


class MeshVolumeElementParser(FluidParser):
    keyword = '*MESH_VOLUME_ELEMENT'
    rows = [["eid","pid","n1","n2","n3","n4"]]
    integers = ["eid","pid","n1","n2","n3","n4"]
    repeat = True
    widths = (8,) * 12

