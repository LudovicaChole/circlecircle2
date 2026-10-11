from .plastic_material_parser import PlasticMaterialParser


class MatModifiedPiecewiseLinearPlasticityParser(PlasticMaterialParser):
    def __init__(self):
        super().__init__('MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY', title=False)
