"""LS-DYNA fixed/free format fields, including parameter and D exponent values."""
import math
import re


def fields(line, widths=(10,) * 8):
    line = line.split('$', 1)[0].rstrip('\r\n')
    if ',' in line:
        result = [v.strip() for v in line.split(',')]
        return (result + [''] * len(widths))[:len(widths)]
    result, start = [], 0
    for width in widths:
        result.append(line[start:start + width].strip())
        start += width
    return result


def number(raw, dataframe, default=0.0, integer=False):
    raw = str(raw).strip()
    if not raw:
        value = default
    elif raw.startswith('&'):
        value = dataframe.parameter[raw[1:]].value
    else:
        raw = raw.replace('D', 'E').replace('d', 'e')
        raw = re.sub(r'(?<=\d)([+-]\d+)$', r'e\1', raw) if 'e' not in raw.lower() else raw
        value = float(raw)
    if not math.isfinite(float(value)):
        raise ValueError(f'Nonfinite LS-DYNA field: {raw}')
    if integer and float(value) != int(value):
        raise ValueError(f'Expected integer LS-DYNA field: {raw}')
    return int(value) if integer else float(value)
