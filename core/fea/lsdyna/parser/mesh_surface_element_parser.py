from .fluid_parser import FluidParser


class MeshSurfaceElementParser(FluidParser):
    keyword = '*MESH_SURFACE_ELEMENT'
    rows = [["eid","pid","n1","n2","n3","n4"]]
    integers = ["eid","pid","n1","n2","n3","n4"]
    repeat = True
    widths = (8,) * 10

