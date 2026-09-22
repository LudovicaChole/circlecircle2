"""PAM entity selections. Card layouts follow the supplied PAM examples.

The vendor's 2023 keyword manual was not available for independent verification.
"""
import math
from core.fea.lsdyna.parser.card_fields import number


def ids(df, values):
    return list(dict.fromkeys(number(v, df, integer=True) for v in values if str(v).strip() and number(v,df,integer=True)))


def field(value, width=8):
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError('Nonfinite PAM field')
        text = str(value)
        if len(text) > width:
            text = next((format(value, f'.{p}g') for p in range(width-2, 0, -1)
                         if len(format(value, f'.{p}g')) <= width), '')
    else:
        text = str(value)
    if not text or len(text) > width:
        raise ValueError(f'PAM field exceeds width {width}: {value}')
    return text.rjust(width)


def selection(kind, values):
    values = list(values)
    if not values:
        raise ValueError(f'Empty PAM {kind} selection')
    lines = []
    for start in range(0, len(values), 7):
        lines.append(f'        {kind:<8}' + ''.join(field(v) for v in values[start:start+7]) + '\n')
    return lines + ['        END\n']


def group_name(kind, sid, obj):
    name = str(getattr(obj, 'name', '')).strip()
    if name in ('', 'default'):
        name = kind
    # Include family and ID: LS-DYNA set namespaces may reuse the same integer.
    name = name.replace("'", '_').replace('\n', '_').replace('\r', '_')[:48]
    return f'{name}_{kind}_{sid}'


def resolve(df, sid, styp):
    stores = {1: ('shell', 'set_shell_list'), 2: ('part', 'set_part_list'), 4: ('node', 'set_node_list')}
    if styp in stores:
        kind, key = stores[styp]
        obj = df.storge[key][sid]
        return [f"        GRP '{group_name(kind,sid,obj)}'\n", '        END\n']
    if styp == 3:
        if sid not in df.part:
            raise ValueError(f'Missing contact part {sid}')
        return selection('PART',[sid])
    if styp == 5:
        return selection('PART', sorted(df.part))
    if styp == 6:
        excluded = set(ids(df,df.set_part_list[sid].ids))
        return selection('PART', sorted(set(df.part)-excluded))
    raise ValueError(f'Contact SSTYP/MSTYP={styp}, ID={sid}: no lossless PAM selection implemented')
