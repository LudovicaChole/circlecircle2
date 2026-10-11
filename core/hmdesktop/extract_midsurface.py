"""Native midsurface extraction with explicit selection and output validation."""
from .tcl_bridge import ids, mark, run


def extract_midsurface(solid, method=3):
    before = set(ids('surfs'))
    mark('solids', [solid])
    run(f'*midsurface_extract_10 solids 1 3 0 0 1 {method} 0 2 0 0 10 0 0 0.5 undefined 0 0 1')
    created = sorted(set(ids('surfs')) - before)
    if not created:
        raise ValueError(f'Solid {solid}: midsurface extraction produced no surfaces.')
    return created
