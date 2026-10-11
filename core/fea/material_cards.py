"""Source material fingerprints. All offsets are solver card columns, not tokens."""
import re
from contextlib import contextmanager
from utilities.source_location import source_location as _source_location, diagnostic
from contextvars import ContextVar

_material_sources = ContextVar("material_sources", default={})


def source_location(path=None, line=None, keyword=None):
    path, line = _material_sources.get().get(line, (path, line))
    return _source_location(path, line, keyword)

from types import SimpleNamespace

from core.fea.dataframe import dataframe
from core.fea.lsdyna.parser.card_fields import fields, number


# Add a keyword and its reference card/column here to share recognition logic.
MATERIAL_KEYWORDS = {
    '*MAT_JOHNSON_COOK': None,
    '*MAT_015': None,
    '*MAT_15': None,
    '*MAT_PIECEWISE_LINEAR_PLASTICITY': (1, 2),
    '*MAT_PIECEWISE_LINEAR_PLASTICITY_LOG_INTERPOLATION': (1, 2),
    '*MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY': (1, 2),
    '*MAT_BARLAT_YLD2000': (1, 5),
    '*MAT_ELASTIC': None,
    '*MAT_RIGID': None,
}


def numeric(raw, default=0, integer=False):
    return number(raw, dataframe, default, integer=integer)



class SourceRows(list):
    def __init__(self, values, source_line):
        super().__init__(values)
        self.source_line = source_line


@contextmanager
def material_source(path, line, keyword):
    location = source_location(path, line, keyword)
    try:
        yield location
    except (ValueError, IndexError, KeyError) as error:
        raise ValueError(diagnostic(error, location)) from error


def dyna_blocks(text):
    blocks, current = [], None
    for source_line, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith('$'):
            continue
        if line.startswith('*'):
            current = [line.strip().upper(), SourceRows([], source_line)]
            blocks.append(current)
        elif current is not None:
            current[1].append(line)
    return blocks


def titled(keyword, rows):
    title = rows[0].strip() if keyword.endswith('_TITLE') else None
    return title, rows[1:] if title is not None else rows


def read_lsdyna(text, file_path=None):
    blocks = dyna_blocks(text)
    curves, tables, materials = {}, {}, []
    for keyword, rows in blocks:
        if not keyword.startswith(('*DEFINE_CURVE', '*DEFINE_TABLE')):
            continue
        with material_source(file_path, rows.source_line, keyword) as location:
            title, cards = titled(keyword, rows)
            if not cards:
                continue
            if keyword.startswith('*DEFINE_CURVE'):
                h = fields(cards[0])
                cid = numeric(h[0], integer=True)
                points = [tuple(numeric(v) for v in fields(r, (20, 20))) for r in cards[1:] if r.strip()]
                curves[cid] = dict(id=cid, title=title,
                                   scale=(numeric(h[2], 1), numeric(h[3], 1)),
                                   offset=(numeric(h[4]), numeric(h[5])), points=points)
            elif keyword.startswith('*DEFINE_TABLE'):
                tid = numeric(fields(cards[0])[0], integer=True)
                tables[tid] = [(numeric(v[0]), numeric(v[1], integer=True))
                               for r in cards[1:] if r.strip() for v in [fields(r, (20, 20))]]
    for keyword, rows in blocks:
        with material_source(file_path, rows.source_line, keyword) as location:
            base = keyword.removesuffix('_TITLE')
            if base not in MATERIAL_KEYWORDS:
                continue
            title, cards = titled(keyword, rows)
            h = fields(cards[0])
            mid = numeric(h[0], integer=True)
            refpos = MATERIAL_KEYWORDS[base]
            ref = numeric(fields(cards[refpos[0]])[refpos[1]], integer=True) if refpos else 0
            if base == '*MAT_BARLAT_YLD2000' and ref > 0:
                ref = 0  # Positive HARD selects a law; only negative HARD references a curve.
            cid, table = abs(ref), None
            if cid in tables:
                table = tables[cid]
                cid = min(table, key=lambda pair: pair[0])[1] if table else 0
            fingerprint = dict(keyword=base, title=title, id=mid, rho=numeric(h[1]),
                               e=numeric(h[2]), pr=numeric(h[3]), reference=ref,
                               table=table, curve=curves.get(cid))
            johnson_cook = base in ('*MAT_JOHNSON_COOK', '*MAT_015', '*MAT_15')
            if johnson_cook:
                if len(cards) < 4:
                    raise ValueError('Incomplete MAT_JOHNSON_COOK: expected at least four data cards')
                fingerprint.update(keyword='*MAT_JOHNSON_COOK', e=numeric(h[3]), pr=numeric(h[4]),
                                   cards=[tuple(numeric(v) for v in fields(card)) for card in cards])
            materials.append(SimpleNamespace(uid=mid, name=title or f'mat_{mid}',
                             rho=fingerprint['rho'], e=fingerprint['e'], pr=fingerprint['pr'],
                             tag='rigid' if base == '*MAT_RIGID' else ('plastic' if refpos or johnson_cook else 'elastic'),
                             source_solver='lsdyna', fingerprint=fingerprint, map_tag=None, source_context=location))
    return materials


def pam_blocks(text):
    from core.fea.include_reader import pam_keyword
    blocks, current = [], None
    encrypted = False
    for source_line, line in enumerate(text.splitlines(), 1):
        if line.startswith('SECURE'):
            encrypted, current = True, None
        if encrypted:
            if line.strip().startswith('END_SECURE'):
                encrypted = False
            continue
        if line.lstrip().startswith('$'):
            continue
        if line.strip().startswith('END'):
            current = None
            continue
        if pam_keyword(line) and not line[:8].strip().endswith('/'):
            current = None
            continue
        if line[:8].strip().endswith('/'):
            current = [line[:8].strip(), SourceRows([line], source_line)]
            blocks.append(current)
        elif current is not None:
            current[1].append(line)
    return blocks


def read_pamcrash(text, file_path=None):
    from core.fea.pamcrash.parser.card_fields import value as pam_value

    def require_rows(rows, count, description):
        if len(rows) < count:
            raise ValueError(f'{description}: incomplete cards; expected at least {count} rows, got {len(rows)}')

    blocks, curves, materials = pam_blocks(text), {}, []
    for keyword, rows in blocks:
        with material_source(file_path, rows.source_line, keyword) as location:
            if keyword != 'FUNCT /':
                continue
            require_rows(rows, 3, 'FUNCT')
            h = rows[0]
            cid = pam_value(h[8:16], integer=True)
            if cid <= 0:
                raise ValueError('FUNCT: a positive IDFUN is required')
            points = [(pam_value(r[16:32]), pam_value(r[32:48])) for r in rows[2:] if r.strip()]
            if not points:
                raise ValueError(f'FUNCT {cid}: no points')
            curves[cid] = dict(id=cid, title=rows[1][5:].strip(),
                               scale=(pam_value(h[24:32], default=1), pam_value(h[32:40], default=1)),
                               offset=(pam_value(h[40:48]), pam_value(h[48:56])), points=points)
    for keyword, rows in blocks:
        with material_source(file_path, rows.source_line, keyword) as location:
            if keyword != 'MATER /':
                continue
            h = rows[0]
            mid, matyp = pam_value(h[8:16], integer=True), pam_value(h[16:24], integer=True)
            if mid <= 0:
                raise ValueError('MATER: a positive IDMAT is required')
            if matyp not in (1, 100, 103, 105):
                raise ValueError(f'PAM material {mid}: unsupported MATYP {matyp}')
            require_rows(rows, 5 if matyp == 1 else 4, f'PAM material {mid} (MATYP{matyp})')
            title, rho = rows[2][5:].strip() or f'mat_{mid}', pam_value(h[24:40])
            if matyp == 1:
                g, k = pam_value(rows[3][:10]), pam_value(rows[4][:10])
                if g <= 0 or k <= 0:
                    raise ValueError(f'PAM material {mid}: positive G and K are required')
                e, pr = 9*k*g/(3*k+g), (3*k-2*g)/(2*(3*k+g))
            else:
                e, pr = pam_value(rows[3][:10]), pam_value(rows[3][20:30])
            if rho <= 0 or e <= 0 or not -1 < pr < .5:
                raise ValueError(f'PAM material {mid}: invalid density or isotropic elastic properties')
            # Solid MATYP=1 has several laws. CURVE uses cards after G and K;
            # treating all type-1 materials as elastic silently drops plasticity.
            law = rows[3][10:20].strip().upper() if matyp == 1 else ''
            ref_row = 5 if matyp == 1 and law == 'CURVE' else (4 if matyp == 105 else None)
            if ref_row is not None:
                require_rows(rows, ref_row+2, f'PAM material {mid}: curve references and strain rates')
            refs = [pam_value(v, integer=True) for v in fields(rows[ref_row])] if ref_row is not None else []
            rates = [pam_value(v) for v in fields(rows[ref_row+1])] if ref_row is not None else []
            for cid in refs:
                if cid and abs(cid) not in curves:
                    raise ValueError(f'PAM material {mid}: undefined FUNCT {cid}')
            curve_data = [curves.get(abs(cid)) for cid in refs if cid]
            fingerprint = dict(keyword=f'MATYP{matyp}', title=title, id=mid, rho=rho, e=e, pr=pr,
                               references=refs, rates=rates, curves=curve_data, source_rows=list(rows))
            # Blank law fields may define an inline plastic point law, not an
            # elastic material. Keep its classification even when no library
            # curve is available; the exporter must report nonlinear fallback.
            inline_plastic = matyp == 1 and not law and len(rows) > 6 and any(
                pam_value(v) for v in fields(rows[6]))
            materials.append(SimpleNamespace(uid=mid, name=title, rho=rho, e=e, pr=pr,
                             tag='plastic' if matyp in (103, 105) or law or inline_plastic else 'elastic', source_solver='pamcrash',
                             fingerprint=fingerprint, map_tag=None, source_context=location))
    return materials


def read_abaqus(text, file_path=None):
    materials, current, section = [], None, None
    lines = text.splitlines()
    # Join keyword continuations in place, retaining original line positions.
    for index in range(len(lines)):
        if not lines[index].lstrip().startswith('*') or lines[index].lstrip().startswith('**'):
            continue
        cursor = index
        while lines[index].rstrip().endswith(','):
            cursor += 1
            if cursor >= len(lines):
                raise ValueError(diagnostic('Incomplete Abaqus keyword continuation', source_location(file_path, index+1)))
            tail = lines[cursor].strip()
            if not tail or tail.startswith('**'):
                continue
            if tail.startswith('*'):
                raise ValueError(diagnostic('Incomplete Abaqus keyword continuation', source_location(file_path, index+1)))
            lines[index] = lines[index].rstrip() + tail
            lines[cursor] = ''
    for source_line, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith('**'):
            continue
        if line.startswith('*'):
            section = line.split(',')[0].strip().upper()
            if section == '*ELASTIC':
                match = re.search(r'\bTYPE\s*=\s*([^,]+)', line, re.I)
                if match and match[1].strip().upper() != 'ISOTROPIC':
                    raise ValueError(diagnostic('Only isotropic ELASTIC materials can use the elastic fallback',
                                                source_location(file_path, source_line, section)))
            if section == '*MATERIAL':
                match = re.search(r'\bNAME\s*=\s*("[^"]*"|[^,]+)', line, re.I)
                if not match:
                    raise ValueError(diagnostic('Abaqus material has no NAME', source_location(file_path, source_line, section)))
                name = match[1].strip().strip('"')
                current = SimpleNamespace(uid=len(materials)+1, name=name, tag='elastic', rho=None,
                                          source_solver='abaqus', map_tag=None,
                                          source_context=source_location(file_path, source_line, section),
                                          fingerprint={'keyword': 'STATIC_PLASTIC', 'title': name, 'plastic': []})
                materials.append(current)
            elif section not in ('*DENSITY', '*ELASTIC', '*PLASTIC'):
                current = None
            continue
        if current is None:
            continue
        with material_source(file_path, source_line, section):
            vals = [numeric(v) for v in line.split(',') if v.strip()]
            if section == '*DENSITY':
                current.rho = vals[0]
                current.fingerprint['rho'] = vals
            elif section == '*ELASTIC':
                current.e, current.pr = vals[:2]
                current.fingerprint['elastic'] = vals
            elif section == '*PLASTIC':
                current.tag = 'plastic'
                current.fingerprint['plastic'].append(vals)
    for material in materials:
        if not all(hasattr(material, key) for key in ('e', 'pr')):
            raise ValueError(diagnostic(f'Abaqus material {material.name}: isotropic ELASTIC is required', material))
    return materials


READERS = {'lsdyna': read_lsdyna, 'pamcrash': read_pamcrash, 'abaqus': read_abaqus}


def register_materials(text, solver, file_path=None, source_map=None):
    dataframe.solver = solver
    token = _material_sources.set(source_map or {})
    try:
        materials = READERS[solver](text, file_path=file_path)
    finally:
        _material_sources.reset(token)
    for material in materials:
        existing = dataframe.material.get(material.uid)
        if existing is not None:
            if file_path and not getattr(existing, "source_context", None):
                existing.source_context = material.source_context
            existing.source_solver = solver
            existing.fingerprint = material.fingerprint
        else:
            dataframe.material[material.uid] = material
            dataframe.storge_material_id.append(material.uid)
