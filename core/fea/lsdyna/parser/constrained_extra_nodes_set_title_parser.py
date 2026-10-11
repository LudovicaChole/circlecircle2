from .constrained_extra_nodes_set_parser import ConstrainedExtraNodesSetParser


class ConstrainedExtraNodesSetTitleParser(ConstrainedExtraNodesSetParser):
    def __init__(self):
        super().__init__(title=True)
