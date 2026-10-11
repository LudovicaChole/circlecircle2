from .plastic_material_parser import PlasticMaterialParser


class MatBarlatYld2000TitleParser(PlasticMaterialParser):
    def __init__(self):
        super().__init__('MAT_BARLAT_YLD2000', title=True)
