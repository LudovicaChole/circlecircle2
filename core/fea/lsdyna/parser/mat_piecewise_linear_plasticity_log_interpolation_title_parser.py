from .plastic_material_parser import PlasticMaterialParser


class MatPiecewiseLinearPlasticityLogInterpolationTitleParser(PlasticMaterialParser):
    def __init__(self):
        super().__init__('MAT_PIECEWISE_LINEAR_PLASTICITY_LOG_INTERPOLATION', title=True)
