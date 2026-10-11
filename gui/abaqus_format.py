"""Display metadata for Abaqus comma-delimited input (SIMULIA Keywords Guide).

References and supported variants are recorded in help_documentation/solver_editors.md.
This is not a solver parser: unknown variants retain generic numbered fields.
"""
from dataclasses import dataclass, replace
from gui.lsdyna_format import Row, comma_spans


@dataclass(frozen=True)
class State:
    keyword: str = ''
    parameters: tuple = ()
    continuation: bool = False
    card: int = 0
    next_node: int = 0


def normalized(text):
    return ''.join(text.upper().split())


def parameter_items(text):
    result = {}
    for a, b in comma_spans(text):
        key, _, value = text[a:b].partition('=')
        if key.strip():
            result[normalized(key)] = normalized(value)
    return result


def free_row(text, keyword, names=(), kind='free', note=''):
    spans = comma_spans(text)
    labels = tuple(names[i] if i < len(names) else f'Field {i + 1}' for i in range(len(spans)))
    issues = []
    if len(text.rstrip()) > 256:
        issues.append('Line exceeds 256 characters')
    if not text.isascii():
        issues.append('Keyword/data input requires ASCII characters')
    return Row(keyword, 'Comma-separated', kind, names=labels,
               note='; '.join(filter(None, (note, *issues))), spans=spans)


def material_labels(base, params, card):
    try:
        dependencies = int(params.get('DEPENDENCIES', '0'))
    except ValueError:
        return (), 0
    if not 0 <= dependencies <= 128:
        return (), 0
    names = tuple(base) + tuple(f'Field variable {i + 1}' for i in range(dependencies))
    count = max(1, (len(names) + 7) // 8)
    phase = card % count
    return names[phase * 8:(phase + 1) * 8], (phase + 1) % count


def scan_line(text, state):
    stripped = text.lstrip()
    if stripped.startswith('**'):
        return Row(state.keyword, 'Comma-separated', 'comment', note='Comment'), state
    if not stripped:
        return Row(state.keyword, 'Comma-separated', note='Blank line'), state
    if stripped.startswith('*') or state.continuation:
        new_keyword = stripped.startswith('*')
        spans = comma_spans(text)
        first_end = spans[0][1]
        key = normalized(text[:first_end]) if new_keyword else state.keyword
        params = {} if new_keyword else dict(state.parameters)
        params.update(parameter_items(text[first_end + 1:] if new_keyword else text))
        # Only semantic switches affect data layouts. Names/paths must not create
        # unique states for every mesh block in a large input deck.
        relevant = {'SYSTEM', 'TYPE', 'GENERATE', 'ELSET', 'DEPENDENCIES', 'HARDENING',
                    'DATATYPE', 'DEFINITION', 'PHANTOM', 'SUBMODEL', 'LOADCASE', 'FILE'}
        params = {k: v for k, v in params.items() if k in relevant}
        for flag in ('ELSET', 'FILE'):
            if flag in params:
                params[flag] = ''
        names = tuple('Keyword' if new_keyword and i == 0 else
                      text[a:b].partition('=')[0].strip() or 'Continuation'
                      for i, (a, b) in enumerate(spans))
        row = free_row(text, key, names, 'keyword', 'Keyword continuation' if not new_keyword else '')
        return row, State(key, tuple(sorted(params.items())), text.rstrip().endswith(','))
    key, params = state.keyword, dict(state.parameters)
    if key in ('*HEADING', '*PARAMETER'):
        return Row(key, 'Text', 'title', note='Heading' if key == '*HEADING' else 'Parameter expression'), state
    names, next_card, next_node = (), 0, 0
    spans = comma_spans(text)
    count = len(spans)
    if key == '*NODE':
        coords = {'R': ('X', 'Y', 'Z'), 'C': ('R', 'Theta', 'Z'),
                  'S': ('R', 'Theta', 'Phi')}.get(params.get('SYSTEM', 'R'))
        if coords:
            names = ('Node ID',) + coords + ('Normal 1', 'Normal 2', 'Normal 3')
    elif key == '*ELEMENT':
        if state.next_node:
            names = tuple(f'Node {state.next_node + i}' for i in range(count))
            next_node = state.next_node + count - 1
        else:
            names = ('Element ID',) + tuple(f'Node {i}' for i in range(1, count))
            next_node = count - 1
        if not text.rstrip().endswith(','):
            next_node = 0
        else:
            names = names[:-1] + ('Continuation',)
    elif key in ('*NSET', '*ELSET'):
        if key == '*NSET' and 'ELSET' in params:
            names = ()
        elif 'GENERATE' in params:
            names = ('First ID', 'Last ID', 'Increment')
        else:
            names = tuple(f'ID / set {i + 1}' for i in range(count))
    elif key == '*ELASTIC':
        base = {'ISOTROPIC': ('E', 'Poisson ratio', 'Temperature'),
                'ENGINEERINGCONSTANTS': ('E1', 'E2', 'E3', 'Nu12', 'Nu13', 'Nu23', 'G12', 'G13', 'G23', 'Temperature'),
                'LAMINA': ('E1', 'E2', 'Nu12', 'G12', 'G13', 'G23', 'Temperature'),
                'SHEAR': ('G', 'Temperature')}.get(params.get('TYPE', 'ISOTROPIC'))
        # A single string may name a distribution instead of numeric constants.
        first = text[spans[0][0]:spans[0][1]].strip()
        if base and (count > 1 or first[:1] in '+-.0123456789<'):
            names, next_card = material_labels(base, params, state.card)
    elif key == '*DENSITY':
        first = text[spans[0][0]:spans[0][1]].strip()
        if count == 1 and first[:1] not in '+-.0123456789<':
            names = ('Distribution',)
        else:
            names, next_card = material_labels(('Density', 'Temperature'), params, state.card)
    elif key == '*PLASTIC':
        hardening = params.get('HARDENING', 'ISOTROPIC')
        if hardening in ('ISOTROPIC', 'KINEMATIC') or (
                hardening == 'COMBINED' and params.get('DATATYPE', 'HALFCYCLE') == 'HALFCYCLE'):
            names, next_card = material_labels(('Yield stress', 'Plastic strain', 'Temperature'), params, state.card)
        elif hardening == 'JOHNSONCOOK':
            names = ('A', 'B', 'n', 'm', 'Melt temp.', 'Transition temp.')
    elif key == '*BOUNDARY' and not {'PHANTOM', 'SUBMODEL'} & params.keys():
        second = text[spans[1][0]:spans[1][1]].strip().upper() if count > 1 else ''
        if second in ('XSYMM', 'YSYMM', 'ZSYMM', 'XASYMM', 'YASYMM', 'ZASYMM', 'PINNED', 'ENCASTRE'):
            names = ('Node / set', 'Constraint type')
        else:
            names = ('Node / set', 'First DOF', 'Last DOF', 'Magnitude')
    elif key == '*CLOAD' and not {'LOADCASE', 'FILE'} & params.keys():
        second = text[spans[1][0]:spans[1][1]].strip().upper() if count > 1 else ''
        if second in ('TSB', 'TFD', 'TWD', 'TSI') or state.card == -1:
            next_card = -1  # Uncatalogued Aqua multi-line loads.
        else:
            names = ('Node / set', 'DOF', 'Magnitude')
    elif key == '*AMPLITUDE':
        definition = params.get('DEFINITION', 'TABULAR')
        if definition in ('TABULAR', 'SMOOTHSTEP'):
            names = tuple(f'{"Time/freq." if i % 2 == 0 else "Amplitude"} {i // 2 + 1}' for i in range(count))
        elif definition == 'EQUALLYSPACED':
            names = tuple(f'Amplitude {i + 1}' for i in range(count))
    note = '' if names else 'Generic fields; keyword / option labels are not in the guide catalog'
    return free_row(text, key, names, note=note), replace(state, card=next_card, next_node=next_node)
