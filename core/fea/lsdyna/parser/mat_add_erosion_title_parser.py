from .mat_add_erosion_parser import MatAddErosionParser


class MatAddErosionTitleParser(MatAddErosionParser):
    def __init__(self):
        super().__init__(title=True)
