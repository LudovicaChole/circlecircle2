"""Import HM/STEP into an isolated batch session and select LS-DYNA."""
from pathlib import Path
from .tcl_bridge import run


def load_geometry(model, source):
    source = Path(source)
    if source.suffix.lower() == '.hm':
        model.readfile(filename=str(source), load_cad_geometry_as_graphics=0)
    elif source.suffix.lower() in ('.stp', '.step'):
        model.geomimport(translator_type='step_ct', input_file_name=str(source),
                         options=['CreationType=Parts', 'ImportFreeCurves=on',
                                  'ImportFreePoints=on', 'SplitComponents=Body', 'TargetUnits=CAD'])
    else:
        raise ValueError('hwx_mesh accepts HM files; STEP is supported for batch validation.')
    run('hm_framework loaduserprofile LsDyna')
