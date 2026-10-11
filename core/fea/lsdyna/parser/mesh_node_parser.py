from .fluid_parser import FluidParser


class MeshNodeParser(FluidParser):
    keyword = '*MESH_NODE'
    rows = [["nid","x","y","z"]]
    integers = ["nid"]
    repeat = True
    widths = (8, 16, 16, 16, 8, 8)

