"""Rescale library plastic stress curves and rate axes into model units."""
from core.fea.material_units import factors
from core.fea.material_cards import READERS, dyna_blocks, titled, fields, numeric
from core.fea.material_catalog import replace_field


def scale_template(text, solver, source_unit):
    scale = factors(source=source_unit)
    stress, rate = scale['stress'], scale['rate']
    if stress == rate == 1:
        return text
    lines = text.splitlines()
    material = READERS[solver](text)[0]
    if solver == 'abaqus':
        section = ''
        for i, line in enumerate(lines):
            if line.startswith('**'):
                continue
            if line.startswith('*'):
                section = line.split(',')[0].strip().upper()
            elif line.strip() and section == '*PLASTIC':
                values = line.split(',')
                values[0] = str(numeric(values[0])*stress)
                if len(values) > 3 and values[3].strip():
                    values[3] = str(numeric(values[3])*rate)
                lines[i] = ', '.join(values)
    elif solver == 'pamcrash':
        refs = {abs(v) for v in material.fingerprint['references'] if v}
        kind, row, matyp = '', 0, int(material.fingerprint['keyword'][5:])
        for i, line in enumerate(lines):
            if line.lstrip().startswith('$'):
                continue
            if line[:8].strip().endswith('/'):
                kind, row = line[:8].strip(), 0
            else:
                row += 1
            if kind == 'FUNCT /' and row == 0 and numeric(line[8:16], integer=True) in refs:
                line = replace_field(line, 32, 8, numeric(line[32:40], default=1)*stress)
                line = replace_field(line, 48, 8, numeric(line[48:56])*stress)
            elif kind == 'MATER /' and row == (6 if matyp == 1 else 5):
                for col, raw in enumerate(fields(line)):
                    if raw:
                        line = replace_field(line, col*10, 10, numeric(raw)*rate)
            lines[i] = line
    else:
        fp = material.fingerprint
        tables = {abs(fp.get('reference', 0))} if fp.get('table') else set()
        stress_curves = ({abs(cid) for _, cid in fp['table']} if fp.get('table') else
                         {abs(fp.get('reference', 0))})
        keyword, row = '', 0
        for i, line in enumerate(lines):
            if line.lstrip().startswith('$'):
                continue
            if line.startswith('*'):
                keyword, row = line.strip().upper(), -1 if line.strip().upper().endswith('_TITLE') else 0
                continue
            base = keyword.removesuffix('_TITLE')
            if base.startswith('*DEFINE_CURVE') and row == 0 and numeric(fields(line)[0], integer=True) in stress_curves:
                line = replace_field(line, 30, 10, numeric(fields(line)[3], default=1)*stress)
            elif base.startswith('*DEFINE_TABLE') and row == 0 and numeric(fields(line)[0], integer=True) in tables:
                line = replace_field(line, 10, 10, numeric(fields(line)[1], default=1)*rate)
                line = replace_field(line, 20, 10, numeric(fields(line)[2])*rate)
            elif base.startswith('*MAT_') and row == 0 and 'PIECEWISE_LINEAR' in base:
                for col in (4, 5):
                    if fields(line)[col]:
                        line = replace_field(line, col*10, 10, numeric(fields(line)[col])*stress)
                if fields(line)[7]:
                    line = replace_field(line, 70, 10, numeric(fields(line)[7])*scale['time'])
            elif base.startswith('*MAT_') and row == 1 and 'PIECEWISE_LINEAR' in base:
                if fields(line)[0]:
                    line = replace_field(line, 0, 10, numeric(fields(line)[0])*rate)
            lines[i] = line
            row += 1
    return '\n'.join(lines).rstrip()+'\n'
