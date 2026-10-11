"""Material dimensions; source model coordinates and values retain their units.

Library units are declared per solver in library_units.json.
Only library dimensional values are rescaled into the selected model units.
"""
from contextvars import ContextVar

MODEL_UNITS = ('kg/mm/ms/J', 'T/mm/s/mJ')

UNIT_SYSTEMS = {
    'kg/mm/ms/J': (1.0, 1e-3, 1e-3),
    'T/mm/s/mJ': (1e3, 1e-3, 1.0),
    'KG/mm/ms/J': (1.0, 1e-3, 1e-3),
    'g/mm/ms/N-mm': (1e-3, 1e-3, 1e-3),
    'tonne/mm/s/N-mm': (1e3, 1e-3, 1.0),
    'KG/m/s/J': (1.0, 1.0, 1.0),
}
def model_unit(value):
    """Migrate supported saved model units; library units remain independent."""
    aliases = {'KG/mm/ms/J': 'kg/mm/ms/J', 'tonne/mm/s/N-mm': 'T/mm/s/mJ'}
    if not isinstance(value, str):
        return MODEL_UNITS[0]
    value = aliases.get(value, value)
    return value if value in MODEL_UNITS else MODEL_UNITS[0]


active_unit = ContextVar('material_unit', default=None)


def selected_unit():
    from utilities.profile_settings import ProfileSettings
    return active_unit.get() or ProfileSettings().preferences()['unit']


def factors(unit=None, source='tonne/mm/s/N-mm'):
    mass, length, time = UNIT_SYSTEMS[unit or selected_unit()]
    sm, sl, st = UNIT_SYSTEMS[source]
    return {'stress': (sm / sl / st**2) / (mass / length / time**2),
            'density': (sm / sl**3) / (mass / length**3),
            'rate': time/st, 'time': st/time}


def physical_points(curve, solver):
    sx, sy = curve.get('scale', (1, 1))
    ox, oy = curve.get('offset', (0, 0))
    if solver == 'pamcrash':
        return [(x*sx+ox, y*sy+oy) for x, y in curve['points']]
    return [((x+ox)*sx, (y+oy)*sy) for x, y in curve['points']]
