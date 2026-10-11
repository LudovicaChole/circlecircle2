from .fluid_parser import FluidParser


class MeshVolumeNodeParser(FluidParser):
    keyword = '*MESH_VOLUME_NODE'
    rows = [["nid","x","y","z"]]
    integers = ["nid"]
    repeat = True
    widths = (8, 16, 16, 16, 16)

