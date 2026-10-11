"""Expand solver-specific includes without losing original source locations."""
from dataclasses import dataclass, field
from pathlib import Path
import os
import re
from core.fea.validation import FeaInputError
from utilities.text_encoding import read_solver_text
from utilities.source_location import source_location


def pam_keyword(line):
    """Recognize both A8 slash cards and documented longer free-format cards."""
    if line.lstrip().startswith('$') or not line.strip():
        return None
    token = line.split()[0]
    if token in ('ACTIVATE_GLOBAL', 'AUTOSLEEP', 'AIRBAGCHECK'):
        return token
    prefix = line[:8].strip()
    if prefix.endswith('/') or line.strip().startswith('END_') or line.strip() == 'ENDDATA' or prefix in ('ANALYSIS', 'TITLE', 'SOLVER', 'UNIT', 'INPUTVER'):
        return prefix
    return None


@dataclass(frozen=True, slots=True)
class SourceLine:
    path: str
    number: int
    text: str

    @property
    def location(self):
        return source_location(self.path, self.number)


@dataclass
class Deck:
    lines: list
    files: list
    _indices: dict = field(default_factory=dict, init=False, repr=False)

    def selected_lines(self, solver, accepts):
        """Keep every block boundary, but visit only relevant data cards.

        Index ranges reference the expanded source records, retaining include
        locations and positional blank cards. Encrypted decks use the original
        stream to preserve all special parser state transitions.
        """
        if solver not in self._indices:
            blocks, start, key, encrypted = [], 0, '', False
            for index, record in enumerate(self.lines):
                line = record.text
                if 'BEGIN PGP MESSAGE' in line or line.startswith('SECURE'):
                    encrypted = True
                header = None
                if solver in ('lsdyna', 'abaqus'):
                    if line.startswith('*') and not (solver == 'abaqus' and line.startswith('**')):
                        header = line.split()[0].upper() if solver == 'lsdyna' else line.split(',')[0].strip().upper()
                else:
                    header = pam_keyword(line)
                if header is not None:
                    if index > start:
                        blocks.append((key,start,index))
                    start,key = index,header
            if start < len(self.lines):
                blocks.append((key,start,len(self.lines)))
            self._indices[solver] = None if encrypted else blocks
        blocks = self._indices[solver]
        if blocks is None:
            yield from self.lines
            return
        for key, start, end in blocks:
            if not key or accepts(key) or (solver == 'abaqus' and self.lines[start].text.rstrip().endswith(',')):
                for index in range(start,end):
                    yield self.lines[index]
            else:
                yield self.lines[start]

    def material_input(self, solver):
        if solver == 'lsdyna':
            accepts = lambda key: key.startswith(('*MAT_', '*DEFINE_CURVE', '*DEFINE_TABLE'))
        elif solver == 'abaqus':
            accepts = lambda key: key in ('*MATERIAL','*DENSITY','*ELASTIC','*PLASTIC') or key.endswith(',')
        else:
            accepts = lambda key: key in ('MATER /','FUNCT /')
        # Build the index once, then discard irrelevant blocks entirely. PAM
        # NODE/SOLID lines are themselves headers, so retaining every header
        # here would still copy almost the entire mesh into the material reader.
        if solver not in self._indices:
            list(self.selected_lines(solver, lambda key: False))
        blocks = self._indices[solver]
        records = []
        if blocks is None:
            records = self.lines
        else:
            previous_material = False
            for key, start, end in blocks:
                selected = accepts(key)
                if selected:
                    records.extend(self.lines[start:end])
                elif previous_material:
                    # End the preceding material context with its real boundary.
                    if solver == 'abaqus' and self.lines[start].text.rstrip().endswith(','):
                        records.extend(self.lines[start:end])
                    else:
                        records.append(self.lines[start])
                previous_material = selected
        return (''.join(record.text for record in records),
                {i:(record.path,record.number) for i,record in enumerate(records,1)})

    @property
    def text(self):
        return ''.join(line.text for line in self.lines)

    @property
    def source_map(self):
        return {i: (line.path, line.number) for i,line in enumerate(self.lines,1)}


def unquote(text):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        return text[1:-1]
    return text


def load_deck(file_path, solver):
    return IncludeReader(file_path, solver).read()


class IncludeReader:
    def __init__(self, file_path, solver):
        self.root = Path(file_path).resolve()
        self.solver = solver
        self.search_paths = []
        self.files = []

    def read(self):
        if self.solver not in ('lsdyna', 'abaqus', 'pamcrash'):
            raise ValueError(f'Unknown include syntax: {self.solver}')
        return Deck(list(self.expand(self.root, ())), self.files)

    def resolve(self, name, source):
        name = unquote(name)
        if not name:
            raise FeaInputError(f'{source.location}: include filename is empty')
        path = Path(name.replace('\\', os.sep).replace('/', os.sep))
        # The selected main deck directory is the conversion job directory.
        # Abaqus INPUT paths use that directory; nested local paths are a fallback.
        bases = [Path(source.path).parent, self.root.parent]
        if self.solver == 'abaqus':
            bases.reverse()
        if self.solver == 'lsdyna' and path.parent == Path('.'):
            bases.extend(self.search_paths)
        candidates = [path] if path.is_absolute() else [base/path for base in bases]
        candidates = list(dict.fromkeys(p.resolve() for p in candidates))
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise FeaInputError(f'{source.location}: include file {name!r} not found; searched: '+
                            '; '.join(str(p) for p in candidates))

    def expand(self, path, active, reference=None):
        path = path.resolve()
        if path in active:
            chain = ' -> '.join(str(p) for p in (*active,path))
            raise FeaInputError(f'{reference.location}: cyclic include: {chain}')
        if len(active) >= 100:
            raise FeaInputError(f'{reference.location}: include nesting exceeds 100 files')
        try:
            text = read_solver_text(path)
        except (OSError, UnicodeError) as error:
            raise FeaInputError(f'{reference.location if reference else path}: cannot read include: {error}') from error
        if path not in self.files:
            self.files.append(path)
        source_path = str(path)
        rows = [SourceLine(source_path,i,line+'\n') for i,line in enumerate(text.splitlines(),1)]
        active = (*active,path)
        if self.solver == 'lsdyna':
            yield from self.dyna(rows,active)
        elif self.solver == 'abaqus':
            yield from self.abaqus(rows,active)
        else:
            yield from self.pam(rows,active)

    @staticmethod
    def paths(rows):
        pending, origin = '', None
        for row in rows:
            text = row.text.strip()
            if not text or text.startswith('$'):
                continue
            if origin is None:
                origin = row
            continued = text.endswith(' +')
            pending += text[:-2] if continued else text
            if not continued:
                yield unquote(pending), origin
                pending, origin = '', None
        if pending:
            raise FeaInputError(f'{origin.location}: incomplete include path continuation')

    def dyna(self, rows, active):
        i = 0
        while i < len(rows):
            row = rows[i]
            if not row.text.lstrip().startswith('*'):
                yield row
                i += 1
                continue
            key = row.text.split('$',1)[0].strip().upper().split(',')[0].split()
            key = key[0] if key else ''
            if key == '*END':
                if len(active) == 1:
                    yield row
                    yield from (tail for tail in rows[i+1:] if not tail.text.strip() or tail.text.lstrip().startswith('$'))
                return
            if key == '*KEYWORD' and len(active) > 1:
                i += 1
                continue
            if key.startswith('*INCLUDE'):
                end = i+1
                while end < len(rows) and not rows[end].text.startswith('*'):
                    end += 1
                if key not in ('*INCLUDE','*INCLUDE_PATH','*INCLUDE_PATH_RELATIVE'):
                    raise FeaInputError(f'{row.location}: {key} requires transformation/offset or other specialised include handling')
                paths = list(self.paths(rows[i+1:end]))
                if not paths:
                    raise FeaInputError(f'{row.location}: {key} has no filename/path')
                for name, origin in paths:
                    if key == '*INCLUDE':
                        yield from self.expand(self.resolve(name,origin),active,origin)
                    else:
                        base = Path(row.path).parent if key.endswith('_RELATIVE') else self.root.parent
                        directory = Path(name.replace('\\',os.sep))
                        self.search_paths.append((base/directory).resolve())
                i = end
                continue
            yield row
            i += 1

    def abaqus(self, rows, active):
        i = 0
        while i < len(rows):
            row = rows[i]
            text = row.text.strip()
            if re.match(r'^\*INCLUDE\s*(?:,|$)',text,re.I):
                while text.endswith(','):
                    i += 1
                    if i >= len(rows) or rows[i].text.lstrip().startswith('*') and not rows[i].text.lstrip().startswith('**'):
                        raise FeaInputError(f'{row.location}: incomplete *INCLUDE parameter line')
                    if rows[i].text.lstrip().startswith('**') or not rows[i].text.strip():
                        continue
                    text += rows[i].text.strip()
                parameters = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)',text)[1:]
                options = {}
                for parameter in parameters:
                    key,sep,value = parameter.partition('=')
                    if not sep or key.strip().upper() in options:
                        raise FeaInputError(f'{row.location}: invalid *INCLUDE parameters')
                    options[key.strip().upper()] = value.strip()
                if set(options) != {'INPUT'}:
                    raise FeaInputError(f'{row.location}: *INCLUDE requires INPUT; encrypted PASSWORD includes are not supported')
                name = options['INPUT']
                if not name.startswith('"'):
                    name = ''.join(name.split())
                yield from self.expand(self.resolve(name,row),active,row)
            else:
                yield row
            i += 1

    def pam(self, rows, active):
        encrypted = False
        for index, row in enumerate(rows):
            text = row.text
            if text.startswith('SECURE'):
                encrypted = True
            if encrypted:
                yield row
                if text.strip().startswith('END_SECURE'):
                    encrypted = False
                continue
            if text[:8].strip() == 'INCLU /':
                yield from self.expand(self.resolve(text[8:].strip(),row),active,row)
            elif text.strip() == 'ENDDATA':
                if len(active) == 1:
                    yield row
                    yield from (tail for tail in rows[index+1:] if not tail.text.strip() or tail.text.lstrip().startswith('$'))
                return
            else:
                # IMPFIL/ imports a mapping file, not an input-deck include.
                yield row
