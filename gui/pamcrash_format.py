"""PAM-CRASH 2020 display layouts transcribed from the supplied photos.

Sources: help_documentation/pamcrash2020/<keyword>.jpg and .pc.
Example-only layouts are explicitly identified in the row note. No solver input
is executed, reformatted or inferred from arbitrary user-file comment headings.
"""
from dataclasses import dataclass, replace
import re
from gui.lsdyna_format import Row


@dataclass(frozen=True)
class State:
    keyword: str = ''
    variant: str = ''
    card: int = 0
    option: str = ''
    meta: bool = False


def layout(ends, names):
    ends = tuple(ends)
    return tuple(b - a for a, b in zip((0,) + ends, ends)), tuple(names.split())


# Inclusive end columns from the photographs; blank regions are real fields.
HEADERS = {
    'NODE': layout((8, 16, 32, 48, 64), 'Keyword IDNOD X Y Z'),
    'SHELL': layout(range(8, 73, 8), 'Keyword IDEL IDPRT IDNOD1 IDNOD2 IDNOD3 IDNOD4 blank H'),
    'SOLID': layout((8, 16, 24), 'Keyword IDEL IDPRT'),
    'TETR4': layout(range(8, 57, 8), 'Keyword IDEL IDPRT IDNOD1 IDNOD2 IDNOD3 IDNOD4'),
    'SPRGBM': layout(range(8, 57, 8), 'Keyword IDEL IDPRT IDNOD1 IDNOD2 IDNOD3 IFRA'),
    'BEAM': layout((8, 16, 24, 32, 40, 48, 58, 64, 66, 72, 80),
                   'Keyword IDEL IDPRT IDNOD1 IDNOD2 IDNOD3 blank DOFCD1 blank DOFCD2 ITPR'),
    'BOUNC': layout((8, 16, 18, 24, 32, 40), 'Keyword IDNOD blank DOFCOD IFRA ISENS'),
    'MTOCO': layout((8, 16, 24, 26, 32, 40, 48, 56, 64, 72),
                    'Keyword IDMTO IDNODi blank DOFCOD IFRA1 ITMTO ISENS ALPHA DOFTYP'),
    'PLINK': layout(range(8, 65, 8), 'Keyword IDELE IDPRT IDNOD1 MORE NLAYR blank IDNOD2'),
    'TIED': layout(range(8, 41, 8), 'Keyword IDEL IDPRT IPCHK IPROJ'),
    'RBODY': layout((8, 16, 24, 32, 40, 56, 64), 'Keyword IDRB blank ITRB IDNODcog blank ISENS'),
    'FRAME': layout((8, 16, 24, 32), 'Keyword IFRA IFRATY IAXIS'),
    'INVEL': layout(range(8, 81, 8), 'Keyword IDNOD VELX0 VELY0 VELZ0 VANX0 VANY0 VANZ0 IFRA IRIGB'),
    'CONLO': layout((8, 16, 24, 32, 40, 48, 56, 64, 80, 81),
                    'Keyword IDNOD IDIR LCUR SFAC IFRA ISENS ILDTYP CLOAD &'),
    'PART': layout(range(8, 65, 8), 'Keyword IDPRT ATYPE IDMAT IDVAMAT IDTHMAT IDPMAT IDNUMPAR'),
    # General definitions are shown in the supplied standard .pc examples.
    'CNTAC': layout((8, 16, 24), 'Keyword IDCTC NTYPE'),
    'MATER': layout((8, 16, 24, 40, 48, 56, 64, 72), 'Keyword IDMAT MATYP RHO ISINT ISHG ISTRAT IFROZ'),
    'FUNCT': layout(range(8, 57, 8), 'Keyword IDFUN FUNTYP SCALX SCALY SHIFTX SHIFTY'),
    'MASS': layout((8, 16, 24, 32, 48, 64, 80), 'Keyword IDNOD IFRA blank DISr DISs DISt'),
    'SENSOR': layout((8, 16, 24, 32, 40), 'Keyword ISENS ITYP ISREV ISOFST'),
    'SECFO': layout((8, 16, 24, 32), 'Keyword IDSF NTYP IFRA'),
    'THELE': layout((8, 16), 'Keyword IDNOD/EL'),
    'TRSFM': layout((8, 16), 'Keyword IDTRSFM'),
    'PYVAR': layout((8, 16), 'Keyword ID'),
}
TEMPLATE_HEADERS = {'CNTAC', 'MATER', 'FUNCT', 'MASS', 'SENSOR', 'SECFO', 'THELE', 'TRSFM', 'PYVAR'}
CONTROLS = set('CCTRL CKCTRL ECTRL EOCTRL MCTRL OCTRL PRCTRL TCTRL RUNEND'.split())
FREE_TOP = set('ANALYSIS AIRBAGCHECK DATACHECK SOLVER INPUTVERSION UNIT'.split())
SELECTION = set('NOD ELE PART GRP OGRP SEG EDG SURF DELNOD DELELE DELPART DELGRP DELOGRP ELE>NOD PART>NOD GRP>NOD ALL END MOVE ROTATE'.split())
FREE_NAMES = {
    'ITER_INIPEN_N': ('Command', 'ITIPNB'), 'ITER_FORCE_N': ('Command', 'NITERA'),
    'ITER_FORCE_EPS': ('Command', 'EPSILON'), 'ANALYSIS': ('Keyword', 'Qualifier'),
    'SOLVER': ('Keyword', 'Qualifier'), 'INPUTVERSION': ('Keyword', 'Version'),
    'UNIT': ('Keyword', 'Length', 'Mass', 'Time', 'Temperature'),
    'AIRBAGCHECK': ('Keyword', 'Switch', 'Qualifier'), 'DATACHECK': ('Keyword', 'Switch', 'Qualifier'),
    'TIME': ('Command', 'End time'), 'MOVE': ('Command', 'Distance', 'Tx', 'Ty', 'Tz', 'Node 1', 'Node 2'),
}

CONTACT33 = (
    layout((10, 20, 30, 40, 45), 'T1SL T2SL ISENS Hcont ITPRT'),
    layout((5, 15, 25, 30, 40, 70, 80), 'IPCP SLFACM FSVNL LIKFOR PENKIN blank TLSTIF'),
    layout((10, 20, 30, 50, 60), 'FRITYP VALUE XDMP1 blank IDCNTPTY'),
    layout((5, 10, 15, 20, 35, 40, 50, 60), 'IRMV IEROD ILEAK IAC32 blank IFRED DTHKPLK ADJTOL'),
    layout((10, 20, 30, 35), 'blank SEPSTR SEPTHK IUPA'),
    layout((5, 15, 25, 45, 55, 75, 80), 'IHTR HTCOND HTSURF blank TSCAL blank IPRES'),
)
CONTACT36 = (
    CONTACT33[0], layout((5, 15, 25, 70, 80), 'IPCP SLFACM FSVNL blank TLSTIF'),
    layout((10, 20, 30), 'FRITYP VALUE XDMP1'),
    layout((5, 10, 15, 20, 30, 35, 40, 50, 60), 'IRMV IEROD ILEAK IAC92 blank IOMIT IFRED DTHKPLK ADJTOL'),
    layout((80,), 'blank'), layout((45, 55, 75, 80), 'blank TSCAL blank IPRES'),
)


def fixed(text, state, spec, note=''):
    widths, names = spec
    if '\t' in text:
        return Row(state.keyword, 'Fixed columns', note='Tab character: column guides disabled; use spaces')
    spans, start = [], 0
    for width in widths:
        spans.append((start, start + width))
        start += width
    return Row(state.keyword, 'Fixed columns', 'data', widths, names, note, tuple(spans))


def tokens(text):
    # Quoted names and parameter expressions are single free-format items.
    return tuple((m.start(), m.end()) for m in re.finditer(r'''"[^"]*"|'[^']*'|<[^>]*>|[^\s]+''', text))


def free(text, state, note='Free-format values; no fixed column spacing'):
    spans = tokens(text)
    command = text[spans[0][0]:spans[0][1]].upper() if spans else ''
    names = FREE_NAMES.get(command, ('Command',))
    names = tuple(names[i] if i < len(names) else f'Value {i}' for i in range(len(spans)))
    return Row(state.keyword, 'Free format', 'free', names=names, spans=spans, note=note)


def unknown(state):
    return Row(state.keyword, 'PAM-CRASH', note='Layout not verified for this card / option; no field guides')


def scan_line(text, state):
    stripped, upper = text.lstrip(), text.strip().upper()
    if state.keyword == 'SECURE' and upper != 'END_SECURE':
        return Row('SECURE', 'Protected text', note='Encrypted block; no field guides'), state
    if stripped.startswith('$'):
        return Row(state.keyword, 'PAM-CRASH', 'comment', note='Comment'), state
    if upper.startswith('END_') or upper == 'ENDDATA':
        if upper == 'END_META':
            return Row(state.keyword, 'Text', 'keyword', note='End metadata'), replace(state, meta=False)
        return Row(upper, 'PAM-CRASH', 'keyword', note='End block'), State()
    if upper.startswith('META') and (upper == 'META' or upper[4:5].isspace()):
        return Row(state.keyword, 'Text', 'keyword', note='Metadata'), replace(state, meta=True)
    if state.meta:
        return Row(state.keyword, 'Text', 'title', note='Metadata'), state
    match = re.match(r'^([A-Za-z][A-Za-z0-9]{0,5})\s*/', text)
    if match:
        key = match[1].upper()
        # Only options which change a later layout belong in the continuation
        # state. Node IDs/coordinates must not create one state per mesh row.
        variant = ''
        if key in ('FRAME', 'RBODY'):
            variant = text[24:32].strip().upper()
        elif key in ('PART', 'CNTAC', 'MATER', 'FUNCT', 'SENSOR'):
            variant = text[16:24].strip().upper()
        option = text[72:80].strip() if key == 'INVEL' else ('&' if text[80:81] == '&' else '')
        new = State(key, variant, option=option)
        if key in ('GROUP', 'TITLE', 'IMPFIL'):
            row = Row(key, 'Text', 'title', note='Group name' if key == 'GROUP' else 'Title / file path')
        elif key in HEADERS:
            spec = HEADERS[key]
            if key == 'PART' and variant not in ('SHELL', 'MEMBR', 'SOLID', 'BSHEL', 'COS3D', 'SPHEL', 'TETRA'):
                spec = (spec[0][:7], spec[1][:7])
            row = (unknown(new) if key == 'RBODY' and variant not in ('', '0') else
                   fixed(text, new, spec, 'Header layout from supplied .pc example' if key in TEMPLATE_HEADERS else ''))
        else:
            row = Row(key, 'PAM-CRASH', 'keyword', note='Block header; data layout not verified')
        return row, new
    if text[:4].upper() in ('NAME', 'RMAT'):
        # NAME is not a numeric card and must not shift following card layouts.
        return Row(state.keyword, 'Text', 'title', note='Title / material name (columns 5-80)'), state
    command = stripped.split(None, 1)[0].upper() if stripped else ''
    if command in FREE_TOP:
        new = State(command)
        return free(text, new), new
    if state.keyword == 'PYVAR':
        return Row('PYVAR', 'Text', note='Parameter expression (display only)'), state
    if state.keyword in CONTROLS:
        return free(text, state), state
    if command in SELECTION:
        return free(text, state, 'Entity selection / transform; quoted names and ranges stay together'), state

    key, card, variant = state.keyword, state.card, state.variant
    spec, note = None, ''
    if key == 'SOLID' and card == 0:
        spec = layout((16,) + tuple(range(24, 81, 8)), 'blank IDNOD1 IDNOD2 IDNOD3 IDNOD4 IDNOD5 IDNOD6 IDNOD7 IDNOD8')
    elif key == 'BEAM' and card < 2:
        n = card + 1
        spec = layout(range(8, 49, 8), f'blank ALPHA{n} BETA{n} GAMMA{n} KSI{n} ETA{n}')
    elif key == 'FRAME':
        if variant in ('1', '3') and card == 0:
            spec = layout((8, 16, 24, 32), 'blank NF1 NF2 NF3')
        elif variant in ('4', '5') and card == 0:
            spec = layout((8, 16, 24), 'blank NF1 NF2')
        elif variant == '0' and card < 2:
            spec = layout((8, 24, 40, 56), 'blank Ux Uy Uz') if card == 0 else layout((8, 24, 40, 56, 64), 'blank Vx Vy Vz IDNOD')
    elif key == 'INVEL' and state.option == '1' and card == 0:
        spec = layout((8, 16, 24, 32, 40), 'blank NRIGB XRIGB YRIGB ZRIGB')
    elif key == 'CONLO' and state.option == '&' and card == 0:
        spec = layout((8, 24, 28), 'blank CLOADi LTYP')
    elif key == 'PART':
        if card < 2:
            spec = layout((10, 20, 30), 'DTELIM TSCALF DTRATIO' if card == 0 else 'TCONT EPSINI COULFRIC')
        elif variant == 'SHELL' and card == 2:
            spec, note = layout((10, 20, 25), 'H OFFSET NTHDO'), 'Layout from supplied part.pc example'
    elif key == 'CNTAC' and variant in ('33', '36') and card < 6:
        spec = (CONTACT33 if variant == '33' else CONTACT36)[card]
    elif key == 'FUNCT' and variant in ('31', '55', '150'):
        return fixed(text, state, layout((16, 32, 48), 'blank X Y'), 'Layout from supplied funct.pc examples'), state
    elif key == 'MASS' and card < 2:
        spec = layout((8, 24, 40, 56), 'blank Mx My Mz' if card == 0 else 'blank Ix Iy Iz')
        note = 'Layout from supplied mass.pc example'
    elif key == 'SENSOR' and variant == '5' and card == 0:
        spec, note = layout((8, 16), 'blank LCS'), 'Layout from supplied sensor.pc example'
    elif key == 'MATER':
        if card == 0:
            spec = layout((8, 16, 24, 32, 40, 48, 56, 64), 'blank AUXID1 AUXID2 AUXID3 AUXID4 AUXID5 AUXID6 QVM')
            note = 'Layout from supplied material examples'
        elif variant == '100' and card == 1:
            spec = layout((10, 20, 30), 'E blank NU')
        elif variant in ('1', '105'):
            note = f'Layout from supplied mater{variant}.pc example'
            if card == 1:
                spec = layout(range(10, 81, 10), 'E LAW NU ALPHA HGM HGW HGQ As') if variant == '105' else layout((10, 20, 30, 40), 'G LAW blank ALPHA')
                state = replace(state, option='CURVE' if text[10:20].strip().upper() == 'CURVE' else 'Other')
            elif state.option == 'CURVE':
                offset = 1 if variant == '1' else 0
                if variant == '1' and card == 2:
                    spec = layout((10, 20), 'K blank')
                elif card == 2 + offset:
                    spec = layout(range(10, 81, 10), 'LC1 LC2 LC3 LC4 LC5 LC6 LC7 LC8')
                elif card == 3 + offset:
                    spec = layout(range(10, 81, 10), 'ERATE1 ERATE2 ERATE3 ERATE4 ERATE5 ERATE6 ERATE7 ERATE8')
                # Later failure-law branches vary; do not guess their layout.
    elif key == 'IMPFIL':
        return Row(key, 'Text', 'title', note='Include path'), state
    after = replace(state, card=min(card + 1, 8))
    return (fixed(text, state, spec, note) if spec else unknown(state)), after
