from .mat_piecewise_linear_plasticity_parser import MatPiecewiseLinearPlasticityParser


class MatPiecewiseLinearPlasticityTitleParser(MatPiecewiseLinearPlasticityParser):
    def __init__(self):
        super().__init__(title=True)
