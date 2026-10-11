"""Thickness-based routing; unknown estimates are never called uniform."""
import math
from .tcl_bridge import mark, run


def classify_geometry(solid, tolerance):
    mark('solids', [solid])
    # Geometric thin-solid query avoids the FE nodes created by the legacy
    # thickness estimator on failed estimates.
    try:
        raw = run('set c2thin [hm_getgeometricthinsolidinfo solids 1 mode=advanced]; '
                  'set c2th {}; foreach row $c2thin {lappend c2th [lindex $row 0]}; set c2th')
    except RuntimeError as error:
        if 'thin solids' in str(error).lower():
            return 'unknown', None
        raise
    samples = [float(v) for v in raw.split()]
    if not samples or not all(math.isfinite(v) and 0 < v < 1e100 for v in samples):
        return 'unknown', None
    bounds = [min(samples), max(samples)]
    return ('sheet' if bounds[1]-bounds[0] <= tolerance else 'variable'), bounds
