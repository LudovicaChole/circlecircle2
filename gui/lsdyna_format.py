"""Display-only LS-DYNA card layouts, based on the R13 keyword manuals.

Vol I: GS 2-27..30; NODE 33-2; ELEMENT 19-60, 19-95..97, 19-115..118;
DEFINE 17-84..85, 17-369; PART 35-4..5; SET 41-37, 41-61.
Unknown cards deliberately have no inferred field boundaries.
"""
from dataclasses import dataclass, replace
import re
from core.fea.lsdyna.em_cards import EM_SCHEMAS


@dataclass(frozen=True)
class State:
    default: str = 'Standard'
    keyword: str = ''
    mode: str = 'Standard'
    card: int = 0
    title: bool = False
    phase: int = 0
    inactive: bool = False


@dataclass(frozen=True)
class Row:
    keyword: str = ''
    mode: str = 'Standard'
    kind: str = 'text'
    widths: tuple = ()
    names: tuple = ()
    note: str = ''
    # Positions are zero-based, half-open character ranges.
    spans: tuple = ()


def fields(widths, names, mode):
    start, spans = 0, []
    for width in widths:
        spans.append((start, start + width))
        start += width
    return tuple(widths), tuple(names), tuple(spans)


def comma_spans(text):
    start, quote, spans = 0, '', []
    for index, char in enumerate(text):
        if char in ('"', "'"):
            quote = '' if quote == char else char if not quote else quote
        elif char == ',' and not quote:
            spans.append((start, index))
            start = index + 1
    spans.append((start, len(text)))
    return tuple(spans)


def numeric_row(state, text, widths, names=(), note=''):
    widths, names, spans = fields(widths, names, state.mode)
    names = names + tuple(f'F{i + 1}' for i in range(len(names), len(widths)))
    if '\t' in text:
        return Row(state.keyword, state.mode, 'text', note='Tab character: fixed-column guides disabled; use spaces.')
    if ',' in text:
        spans = comma_spans(text)
        names = names[:len(spans)] + tuple(f'F{i + 1}' for i in range(len(names), len(spans)))
        return Row(state.keyword, 'Comma-separated', 'free', (), names, note, spans)
    return Row(state.keyword, state.mode, 'data', widths, names, note, spans)


# These cards use the manual's standard 8 x 10 format. Exact names avoid
# silently applying a base keyword's layout to an unrelated option.
STANDARD_CARDS = set('''
CONTROL_ACCURACY CONTROL_BULK_VISCOSITY CONTROL_CONTACT CONTROL_DYNAMIC_RELAXATION
CONTROL_ENERGY CONTROL_OUTPUT CONTROL_PARALLEL CONTROL_RIGID CONTROL_SHELL CONTROL_SOLID
CONTROL_SOLUTION CONTROL_TERMINATION CONTROL_TIMESTEP CONTROL_HOURGLASS
DATABASE_ABSTAT DATABASE_DCFAIL DATABASE_DEFORC DATABASE_DISBOUT DATABASE_ELOUT
DATABASE_GLSTAT DATABASE_JNTFORC DATABASE_MATSUM DATABASE_NODOUT DATABASE_RCFORC
DATABASE_RWFORC DATABASE_SBTOUT DATABASE_SECFORC DATABASE_SLEOUT DATABASE_SWFORC
DATABASE_BINARY_D3PLOT DATABASE_BINARY_INTFOR DATABASE_BINARY_D3THDT DATABASE_BINARY_D3DUMP
DATABASE_BINARY_RUNRSF DATABASE_EXTENT_BINARY DATABASE_FORMAT DATABASE_NODFOR
DATABASE_HISTORY_NODE DATABASE_HISTORY_SHELL DATABASE_HISTORY_SOLID
SECTION_SHELL SECTION_SOLID HOURGLASS
BOUNDARY_PRESCRIBED_MOTION_RIGID BOUNDARY_PRESCRIBED_MOTION_NODE BOUNDARY_PRESCRIBED_MOTION_SET
BOUNDARY_SPC_NODE BOUNDARY_SPC_SET CONSTRAINED_EXTRA_NODES_SET CONSTRAINED_EXTRA_NODES_NODE
CONSTRAINED_NODAL_RIGID_BODY INITIAL_VELOCITY_GENERATION
MAT_ELASTIC MAT_001 MAT_1 MAT_RIGID MAT_020 MAT_20
MAT_PIECEWISE_LINEAR_PLASTICITY MAT_024 MAT_24
MAT_PIECEWISE_LINEAR_PLASTICITY_LOG_INTERPOLATION
MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY MAT_123
MAT_BARLAT_YLD2000 MAT_133 MAT_ADD_EROSION MAT_ADD_DAMAGE_GISSMO
PARAMETER PARAMETER_LOCAL PARAMETER_MUTABLE PARAMETER_LOCAL_MUTABLE
'''.split())

FIRST_NAMES = {
    'MAT_ELASTIC': ('MID', 'RO', 'E', 'PR', 'DA', 'DB', 'K'),
    'MAT_RIGID': ('MID', 'RO', 'E', 'PR', 'N', 'COUPLE', 'M', 'ALIAS'),
    'MAT_PIECEWISE_LINEAR_PLASTICITY': ('MID', 'RO', 'E', 'PR', 'SIGY', 'ETAN', 'FAIL', 'TDEL'),
    'CONTROL_TERMINATION': ('ENDTIM', 'ENDCYC', 'DTMIN', 'ENDENG', 'ENDMAS', 'NOSOL'),
    'CONTROL_TIMESTEP': ('DTINIT', 'TSSFAC', 'ISDO', 'TSLIMT', 'DT2MS', 'LCTM', 'ERODE', 'MS1ST'),
    'SECTION_SHELL': ('SECID', 'ELFORM', 'SHRF', 'NIP', 'PROPT', 'QR/IRID', 'ICOMP', 'SETYP'),
    'SECTION_SOLID': ('SECID', 'ELFORM', 'AET'),
}

CONTACT_CARDS = {'CONTACT_AUTOMATIC_SINGLE_SURFACE', 'CONTACT_AUTOMATIC_SURFACE_TO_SURFACE',
                 'CONTACT_TIED_NODES_TO_SURFACE_OFFSET', 'CONTACT_SINGLE_EDGE'}


def _scan_line(text, state):
    """Return display metadata and a bounded continuation state for the next line."""
    stripped = text.lstrip()
    if stripped.startswith('$'):
        return Row(state.keyword, state.mode, 'comment', note='Comment'), state
    if stripped.startswith('*'):
        header = stripped.split('$', 1)[0].strip().upper()
        disabled = re.fullmatch(r'\*COMMENT\s+(\*[A-Z][A-Z0-9_]*[+%\-]?(?:\s+.*)?)', header)
        inactive = disabled is not None
        if disabled:
            # Display the original card layout without activating the source keyword.
            header = disabled[1]
        token = re.split(r'[\s,]', header, maxsplit=1)[0]
        # LS-PrePost can retain a disabled PART as COMMENTPART or COMMENT PART.
        # This alias is for display only; it must not reactivate the source card.
        if re.fullmatch(r'\*COMMENT\s+PART[+%\-]?', header):
            token = '*COMMENTPART'
        modifier = header[-1] if header[-1:] in ('+', '-', '%') else ''
        token = token.rstrip('+-%')
        default = state.default
        if token == '*KEYWORD' and not inactive:
            long_option = re.search(r'\bLONG\s*=\s*([YSKN])', header)
            i10_option = re.search(r'\bI10\s*=\s*([YN])', header)
            if long_option:
                default = 'Long' if long_option[1] in ('Y', 'K') else 'Standard'
            if i10_option and default != 'Long':
                default = 'I10' if i10_option[1] == 'Y' else 'Standard'
        mode = {'+': 'Long', '-': 'Standard', '%': 'I10'}.get(modifier, default)
        title = token.endswith('_TITLE')
        keyword = token[:-6] if title else token
        next_state = State(default, keyword, mode, title=title, inactive=inactive)
        note = 'Commented-out PART (inactive)' if keyword == '*COMMENTPART' else 'Keyword'
        return Row(token, mode, 'keyword', note=note if text.startswith('*') else 'Keyword should start in column 1'), next_state
    if not state.keyword:
        return Row(note='No keyword context; no field guides'), state
    if state.title:
        return Row(state.keyword, state.mode, 'title', note='Title / heading'), replace(state, title=False)
    if state.mode != 'Standard':
        return Row(state.keyword, state.mode, 'text', note=f'{state.mode} format is not supported by the editor guides yet'), state

    key = state.keyword[1:]
    next_state = replace(state, card=min(state.card + 1, 2))
    if key in EM_SCHEMAS:
        try:
            names, _ = EM_SCHEMAS[key].card(state.card)
        except ValueError:
            return Row(state.keyword, state.mode, 'text', note='Unexpected extra EM card'), state
        return numeric_row(state, text, (10,)*8, names,
                           'Electromagnetic card; blank fields use solver defaults'), replace(state, card=min(state.card+1, 3))
    if key in ('TITLE', 'INCLUDE', 'INCLUDE_PATH', 'INCLUDE_PATH_RELATIVE'):
        return Row(state.keyword, state.mode, 'title', note='Title / file path'), state
    if key in ('NODE', 'NODE_MERGE'):
        return numeric_row(state, text, (8, 16, 16, 16, 8, 8), ('NID', 'X', 'Y', 'Z', 'TC', 'RC')), state
    if key in ('ELEMENT_MASS', 'ELEMENT_MASS_NODE_SET'):
        return numeric_row(state, text, (8, 8, 16, 8), ('EID', 'ID', 'MASS', 'PID')), state
    if key == 'ELEMENT_SHELL':
        return numeric_row(state, text, (8,) * 10, ('EID', 'PID') + tuple(f'N{i}' for i in range(1, 9))), state
    if key == 'ELEMENT_BEAM':
        # R13 Vol I, ELEMENT 19-5: every element occupies one 10 x 8 card.
        return numeric_row(state, text, (8,) * 10,
                           ('EID', 'PID', 'N1', 'N2', 'N3', 'RT1', 'RR1', 'RT2', 'RR2', 'LOCAL')), state
    if key in ('LOAD_NODE_POINT', 'LOAD_NODE_SET'):
        names = ('NID' if key == 'LOAD_NODE_POINT' else 'NSID',
                 'DOF', 'LCID', 'SF', 'CID', 'M1', 'M2', 'M3')
        return numeric_row(state, text, (10,)*8, names), state
    if key in ('DATABASE_HISTORY_BEAM', 'DATABASE_HISTORY_BEAM_SET'):
        # R13 Vol I, DATABASE 16-103..104: repeat eight 10-column IDs.
        return numeric_row(state, text, (10,)*8, tuple(f'ID{i}' for i in range(1,9))), state
    if key == 'DATABASE_HISTORY_BEAM_ID':
        return numeric_row(state, text, (10,70), ('ID','HEADING')), state
    if key == 'SECTION_BEAM':
        # R13 Vol I, SECTION 39-8..15. phase retains ELFORM; card
        # distinguishes the header, dimensions and optional warping card.
        if state.card == 0:
            raw = text.split('$', 1)[0]
            value = (raw.split(',') + [''])[1] if ',' in raw else raw[10:20]
            try:
                form = float(value.strip() or '1')
                form = int(form) if form.is_integer() else 0
            except ValueError:
                form = 0  # Parameter/unknown: do not guess dimension names.
            return numeric_row(state, text, (10,)*8,
                ('SECID','ELFORM','SHRF','QR/IRID','CST','SCOOR','NSM','NAUPD')), replace(state, card=1, phase=form)
        if state.card == 2:
            return numeric_row(state, text, (10,)*8,
                ('YS','ZS','IYR','IZR','IRR','IW','IWR')), replace(state, card=0, phase=0)
        shape = text.lstrip().upper().startswith('SECTION') and state.phase in (2,3,12)
        names = ('STYPE','D1','D2','D3','D4','D5','D6') if shape else {
            1: ('TS1','TS2','TT1','TT2','NSLOC','NTLOC'),
            11: ('TS1','TS2','TT1','TT2','NSLOC','NTLOC'),
            2: ('A','ISS','ITT','J','SA','IST','ITORM'),
            12: ('A','ISS','ITT','J','SA','IST','ITORM'),
            13: ('A','ISS','ITT','J','SA','IST','ITORM'),
            3: ('A','RAMPT','STRESS'),
            4: ('TS1','TS2','TT1','TT2'), 5: ('TS1','TS2','TT1','TT2'),
            7: ('TS1','TS2'), 8: ('TS1','TS2'),
            9: ('TS1','TS2','TT1','TT2','PRINT','ITOFF'),
            14: ('PR','IOVPR','IPRSTR','PR','IOVPR'),
        }.get(state.phase, ())
        row = numeric_row(state, text, (10,)*8, names,
                          '' if names else 'Dimension names depend on ELFORM / material; generic field guides')
        return row, replace(state, card=2 if state.phase == 12 and not shape else 0)
    if key in ('BOUNDARY_SPC_NODE_ID', 'BOUNDARY_SPC_SET_ID'):
        # R13 Vol I, BOUNDARY 5-117..118: repeat ID/heading + constraint.
        if state.phase == 0:
            return numeric_row(state, text, (10, 70), ('ID', 'HEADING')), replace(state, phase=1)
        names = ('NID' if key == 'BOUNDARY_SPC_NODE_ID' else 'NSID',
                 'CID', 'DOFX', 'DOFY', 'DOFZ', 'DOFRX', 'DOFRY', 'DOFRZ')
        return numeric_row(state, text, (10,) * 8, names), replace(state, phase=0)
    if key in ('ELEMENT_SHELL_THICKNESS', 'ELEMENT_SHELL_BETA', 'ELEMENT_SHELL_MCID'):
        if state.phase == 0:
            row = numeric_row(state, text, (8,) * 10, ('EID', 'PID') + tuple(f'N{i}' for i in range(1, 9)))
            # Mid-side nodes require a second thickness card (manual ELEMENT 19-96).
            values = [text[a:b].strip() for a, b in row.spans[6:10]]
            midside = any(value and value not in ('0', '0.0') for value in values)
            return row, replace(state, phase=1, card=1 if midside else 0)
        row = numeric_row(state, text, (16,) * (5 if state.phase == 1 else 4),
                          ('THIC1', 'THIC2', 'THIC3', 'THIC4', 'BETA/MCID') if state.phase == 1
                          else ('THIC5', 'THIC6', 'THIC7', 'THIC8'))
        return row, replace(state, phase=2 if state.phase == 1 and state.card else 0)
    if key == 'ELEMENT_SOLID':
        if state.phase:
            return numeric_row(state, text, (8,) * 8, tuple(f'N{i}' for i in range(1, 9))), replace(state, phase=0)
        row = numeric_row(state, text, (8,) * 10, ('EID', 'PID') + tuple(f'N{i}' for i in range(1, 9)))
        # Standard solids allow either a single EID/PID/N1..N8 row or two rows.
        connectivity = [text[a:b].strip() for a, b in row.spans[2:]]
        if not any(connectivity):
            row = numeric_row(state, text, (8, 8), ('EID', 'PID'), 'Connectivity follows on the next card')
            return row, replace(state, phase=1)
        return row, state
    if key in ('PART', 'COMMENTPART'):
        note = 'Commented-out PART (inactive)' if key == 'COMMENTPART' else ''
        if state.phase == 0:
            return Row(state.keyword, state.mode, 'title', note=note or 'Part heading'), replace(state, phase=1)
        return numeric_row(state, text, (10,) * 8, ('PID', 'SECID', 'MID', 'EOSID', 'HGID', 'GRAV', 'ADPOPT', 'TMID'), note), replace(state, phase=0)
    if key in ('DEFINE_CURVE', 'DEFINE_CURVE_3858', 'DEFINE_CURVE_5434A'):
        if state.card == 0:
            return numeric_row(state, text, (10,) * 8, ('LCID', 'SIDR', 'SFA', 'SFO', 'OFFA', 'OFFO', 'DATTYP', 'LCINT')), next_state
        return numeric_row(state, text, (20, 20), ('A1', 'O1')), next_state
    if key == 'DEFINE_TABLE':
        if state.card == 0:
            return numeric_row(state, text, (10,) * 3, ('TBID', 'SFA', 'OFFA')), next_state
        return numeric_row(state, text, (20,), ('VALUE',)), next_state
    if key in ('SET_NODE_LIST', 'SET_PART_LIST', 'SET_SHELL_LIST', 'SET_SOLID_LIST', 'SET_SEGMENT'):
        names = ('SID', 'DA1', 'DA2', 'DA3', 'DA4', 'SOLVER', 'ITS') if state.card == 0 else (
            ('N1', 'N2', 'N3', 'N4', 'A1', 'A2', 'A3', 'A4') if key == 'SET_SEGMENT' else tuple(f'ID{i}' for i in range(1, 9)))
        return numeric_row(state, text, (10,) * 8, names), next_state
    base_contact = key[:-3] if key.endswith('_ID') else key
    if base_contact in CONTACT_CARDS:
        contact_next = replace(state, card=min(state.card + 1, 4))
        if key.endswith('_ID') and state.card == 0:
            return numeric_row(state, text, (10, 70), ('CID', 'HEADING')), contact_next
        cards = (('SSID', 'MSID', 'SSTYP', 'MSTYP', 'SBOXID', 'MBOXID', 'SPR', 'MPR'),
                 ('FS', 'FD', 'DC', 'VC', 'VDC', 'PENCHK', 'BT', 'DT'),
                 ('SFS', 'SFM', 'SST', 'MST', 'SFST', 'SFMT', 'FSF', 'VSF'))
        index = state.card - int(key.endswith('_ID'))
        names = cards[index] if 0 <= index < len(cards) else ()
        return numeric_row(state, text, (10,) * 8, names), contact_next
    if key in STANDARD_CARDS:
        return numeric_row(state, text, (10,) * 8, FIRST_NAMES.get(key, ()) if state.card == 0 else ()), next_state
    return Row(state.keyword, state.mode, 'text', note='Layout not verified for this keyword / option; no field guides'), next_state


def scan_line(text, state):
    row, next_state = _scan_line(text, state)
    inactive = next_state.inactive if row.kind == 'keyword' else state.inactive
    if inactive:
        note = f'Commented-out {row.keyword} (inactive)'
        if row.note:
            note += '; ' + row.note
        row = replace(row, note=note)
    return row, next_state
