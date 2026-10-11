from .boundary_spc_set_parser import BoundarySpcSetParser


class BoundarySpcSetIdParser(BoundarySpcSetParser):
    def __init__(self):
        super().__init__(with_id=True)
