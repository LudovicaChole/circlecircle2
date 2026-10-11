from .boundary_spc_node_parser import BoundarySpcNodeParser


class BoundarySpcNodeIdParser(BoundarySpcNodeParser):
    def _parse(self, line_raw):
        if self.line_number % 2:
            super()._parse(line_raw)
        self.line_number += 1
