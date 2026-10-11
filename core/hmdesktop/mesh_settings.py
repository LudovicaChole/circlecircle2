"""User workflow defaults, in kg/mm/ms. No HyperMesh imports on the host."""
from dataclasses import dataclass, asdict
import math


@dataclass
class MeshSettings:
    element_size: float = 4.0
    thickness_tolerance: float = 0.01
    density: float = 2.7e-6
    young_modulus: float = 70.0
    poisson_ratio: float = 0.3
    weld_material: str = 'minth_welding_5356'
    weld_width: float = 4.0
    haz_layers: int = 2
    surface_thickness: float | None = None
    timeout_seconds: int = 7200

    def __post_init__(self):
        for name in ('element_size', 'thickness_tolerance', 'density', 'young_modulus',
                     'weld_width', 'timeout_seconds'):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be finite and positive.')
        if not -1 < self.poisson_ratio < 0.5:
            raise ValueError('poisson_ratio must be between -1 and 0.5.')
        if self.surface_thickness is not None and (
                not math.isfinite(self.surface_thickness) or self.surface_thickness <= 0):
            raise ValueError('surface_thickness must be finite and positive.')
        if self.haz_layers != 2:
            raise ValueError('This workflow requires exactly two HAZ rows.')

    def to_dict(self):
        return asdict(self)
