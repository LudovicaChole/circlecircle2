"""Identify materials in the source library and load named target templates."""
import math
from pathlib import Path

from core.fea.dataframe import dataframe
from core.fea.material_cards import READERS, MATERIAL_KEYWORDS, fields, numeric
from core.fea.pamcrash.translator.selection import field
from utilities.logger import logger


def default_catalog_path():
    from utilities.profile_settings import ProfileSettings
    root = Path(ProfileSettings().preferences()['material_library_path'])
    return root if root.name.lower() == 'material_library' else root / 'Material_Library'


def equal_feature(left, right):
    if isinstance(left, (float, int)) and isinstance(right, (float, int)):
        return math.isclose(left, right, rel_tol=1e-8, abs_tol=1e-12)
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(equal_feature(left[k], right[k]) for k in left)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(equal_feature(a, b) for a, b in zip(left, right))
    return left == right


def replace_field(line, start, width, value):
    line = line.ljust(start + width)
    return line[:start] + field(value, width) + line[start + width:]


def load_catalog(file_path=None, solver=None):
    root = Path(file_path) if file_path else default_catalog_path()
    if root.name.lower() != 'material_library' and (root / 'Material_Library').is_dir():
        root = root / 'Material_Library'
    data = {key: {} for key in READERS}
    try:
        if not root.is_dir():
            raise ValueError(f'Material folder is missing: {root}')
        aliases = {'lsdyna': ('lsdyna',), 'abaqus': ('abaqus',), 'pamcrash': ('pamcrash',)}
        for folder in sorted(root.iterdir()):
            normalized = ''.join(c for c in folder.name.lower() if c.isalnum()).removeprefix('material')
            key = next((k for k,v in aliases.items() if normalized in v), None)
            if not folder.is_dir() or key is None:
                continue
            suffixes = {'lsdyna': ('.k', '.key'), 'abaqus': ('.inp', '.inc', '.geo'), 'pamcrash': ('.pc', '.inc')}
            for path in sorted(folder.rglob('*')):
                if path.suffix.lower() not in suffixes[key] or not path.is_file():
                    continue
                try:
                    from utilities.text_encoding import read_solver_text
                    from core.fea.material_templates import material_fragment
                    text = material_fragment(read_solver_text(path), key)
                    records = READERS[key](text)
                    if len(records) != 1:
                        raise ValueError(f'{path}: expected one material and its curves')
                    material = records[0]
                    if not all(math.isfinite(v) for v in (material.e, material.pr)) or material.e <= 0 or not -1 < material.pr < .5:
                        raise ValueError(f'{path}: invalid isotropic elastic properties')
                    if material.tag == 'plastic' and not plastic_curve(material.fingerprint):
                        raise ValueError(f'{path}: unresolved or missing plastic curve')
                    validator = object.__new__(MaterialCatalog)
                    validator.used_ids, validator.next_id = set(), 1
                    getattr(validator, '_render_' + key)(text, material, material.uid)
                    tag = path.relative_to(folder).with_suffix('').as_posix()
                    if tag in data[key]:
                        raise ValueError(f'Duplicate material name: {path}')
                    data[key][tag] = text
                except (OSError, ValueError, UnicodeError, IndexError, KeyError) as error:
                    logger.warning(f'Material template skipped: {path}: {error}')
        if not any(data.values()):
            raise ValueError(f'No valid material files for {solver or "any solver"}: {root}')
        return data
    except (OSError, ValueError, UnicodeError, IndexError, KeyError) as error:
        logger.warning(f'Material library missing or invalid: {error}; all materials use elastic fallback')
        return {key: {} for key in READERS}


def plastic_curve(fingerprint, solver=None):
    """Compare the complete lowest-rate curve in physical coordinates."""
    if not fingerprint:
        return None
    if 'plastic' in fingerprint:
        rows = fingerprint['plastic']
        if not rows:
            return None
        lowest = min((row[3] if len(row) > 3 else 0) for row in rows)
        return [(row[1], row[0]) for row in rows if (row[3] if len(row)>3 else 0) == lowest]
    curve = fingerprint.get('curve')
    if 'curves' in fingerprint:
        pairs = [(rate, candidate) for ref,rate,candidate in zip(
            [r for r in fingerprint.get('references', []) if r],
            [rate for ref,rate in zip(fingerprint.get('references', []), fingerprint.get('rates', [])) if ref],
            fingerprint['curves']) if candidate]
        curve = min(pairs, key=lambda pair: pair[0])[1] if pairs else None
    if not curve or not curve.get('points'):
        return None
    from core.fea.material_units import physical_points
    return physical_points(curve, solver or ('pamcrash' if 'curves' in fingerprint else 'lsdyna'))


class MaterialCatalog:
    def __init__(self, file_path=None, solver='abaqus'):
        self.data = load_catalog(file_path, solver)
        import json
        root = Path(file_path) if file_path else default_catalog_path()
        if (root / 'Material_Library').is_dir():
            root = root / 'Material_Library'
        self.library_units = {'lsdyna': 'KG/mm/ms/J', 'abaqus': 'tonne/mm/s/N-mm', 'pamcrash': 'g/mm/ms/N-mm'}
        if (root / 'library_units.json').is_file():
            self.library_units.update(json.loads((root / 'library_units.json').read_text(encoding='utf-8')))
        self.solver = solver
        from core.fea.material_units import factors
        self.curve_index = {key: {} for key in READERS}
        self.library_materials = {key: {} for key in READERS}
        for source, templates in self.data.items():
            factor = factors(source=self.library_units[source])['stress']
            for tag, text in templates.items():
                candidate = READERS[source](text)[0]
                self.library_materials[source][tag] = candidate
                curve = plastic_curve(candidate.fingerprint, source)
                if curve:
                    normalized = [(x, y*factor) for x, y in curve]
                    self.curve_index[source].setdefault(len(curve), []).append((tag, curve, normalized))
        self.target_materials = self.library_materials[solver]
        self.used_ids = set(dataframe.define_curve) | set(dataframe.define_table)
        self.next_id = 1

    def allocate(self):
        while self.next_id in self.used_ids:
            self.next_id += 1
        result = self.next_id
        self.used_ids.add(result)
        return result

    def render(self, material, mid):
        if material.tag in ('elastic', 'rigid'):
            return None
        if material.rho is None and self.solver != 'abaqus':
            require_density(material, self.solver)
        source = getattr(material, 'source_solver', dataframe.solver)
        fingerprint = getattr(material, 'fingerprint', None)
        actual = plastic_curve(fingerprint, source)
        matches = []
        native_only = set()
        if actual and source in self.curve_index:
            for tag, native, normalized in self.curve_index[source].get(len(actual), []):
                if equal_feature(actual, normalized):
                    matches.append(tag)
                elif equal_feature(actual, native):
                    # Unmodified source-library curves also identify a material.
                    # Unit choice is checked separately, never inferred from its name.
                    matches.append(tag)
                    native_only.add(tag)
        material.map_tag = None
        material.target_map_tag = None
        if len(matches) == 1:
            source_tag = matches[0]
            material.map_tag = Path(source_tag).name
            logger.info(f'Material identified: {mid} ({material.name}) -> {source}.{source_tag}')
            if source_tag in native_only:
                from core.fea.material_units import selected_unit
                logger.warning(f'Material {mid}: curve matches source library units {self.library_units[source]}, '
                               f'but Setting > Unit is {selected_unit()}; verify the source model unit setting', source=material)
            solid = mid in dataframe.storge_pam_elastic_solid_material
            targets = []
            for tag, candidate in self.target_materials.items():
                if Path(tag).name.casefold() != material.map_tag.casefold():
                    continue
                if self.solver == 'pamcrash' and ((candidate.fingerprint['keyword'] == 'MATYP1') != solid):
                    continue
                targets.append(tag)
            if len(targets) == 1:
                material.target_map_tag = targets[0]
                template = self.data[self.solver][targets[0]]
                logger.info(f'Material mapping: {mid} ({material.name}) -> {self.solver}.{targets[0]}')
                template = template.replace('{material_name}', material.name)
                template = template.replace('{material_id}', field(mid, 9 if self.solver == 'pamcrash' else 10))
                from core.fea.material_scaling import scale_template
                template = scale_template(template, self.solver, self.library_units[self.solver])
                return getattr(self, '_render_' + self.solver)(template, material, mid)
            if targets:
                reason = f'source library matched {source_tag}, but multiple {self.solver} templates have filename {material.map_tag}: {", ".join(targets)}'
            else:
                reason = f'source library matched {source_tag}, but no compatible {self.solver} template named {material.map_tag} exists'
        elif matches:
            reason = f'lowest-rate curve matches multiple source-library files: {", ".join(matches)}'
        elif not actual:
            reason = f'no resolved lowest-rate plastic curve is available for source-library matching ({source})'
        elif not self.data.get(source):
            reason = f'no valid {source} templates are available in the source library'
        else:
            reason = f'lowest-rate plastic curve ({len(actual)} points) does not match any {source} source-library template'
        from core.fea.conversion_notes import unconverted
        unconverted(f'Material {mid} ({material.name}): {reason}; nonlinear properties are archived and elastic fallback is used', material)
        return None

    def _render_abaqus(self, template, material, mid):
        lines, section = template.splitlines(), None
        for i, line in enumerate(lines):
            if line.startswith('**'):
                continue
            if line.startswith('*'):
                section = line.split(',')[0].upper()
                if section == '*MATERIAL':
                    lines[i] = f'*MATERIAL, NAME={material.name}'
            elif line.strip() and section in ('*DENSITY', '*ELASTIC'):
                if section == '*DENSITY' and material.rho is None:
                    continue
                values = line.split(',')
                values[:1 if section == '*DENSITY' else 2] = ([str(material.rho)] if section == '*DENSITY'
                                                             else [str(material.e), str(material.pr)])
                lines[i] = ','.join(values)
        return '\n'.join(lines).rstrip() + '\n'

    def _render_pamcrash(self, template, material, mid):
        lines, curve_ids = template.splitlines(), {}
        for line in lines:
            if line.startswith('FUNCT /'):
                old = numeric(line[8:16], integer=True)
                if old in curve_ids:
                    raise ValueError(f'Duplicate FUNCT {old} in material template')
                curve_ids[old] = self.allocate()
        card = None
        row = -1
        for i, line in enumerate(lines):
            if line.lstrip().startswith('$'):
                continue
            if line[:8].strip().endswith('/'):
                card, row = line[:8].strip(), 0
            elif card:
                row += 1
            if card == 'MATER /':
                if row == 0:
                    matyp = numeric(line[16:24], integer=True)
                    lines[i] = replace_field(replace_field(line, 8, 8, mid), 24, 16, material.rho)
                elif row == 2:
                    lines[i] = 'NAME ' + material.name
                elif row == 3 and matyp in (100, 103, 105):
                    lines[i] = replace_field(replace_field(line, 0, 10, material.e), 20, 10, material.pr)
                elif matyp == 1 and row in (3, 4):
                    value = material.e / (2*(1+material.pr)) if row == 3 else material.e / (3*(1-2*material.pr))
                    lines[i] = replace_field(line, 0, 10, value)
                elif (row == 4 and matyp == 105) or (row == 5 and matyp == 1 and law == 'CURVE'):
                    for j, raw in enumerate(fields(line)):
                        old = numeric(raw, integer=True)
                        if old:
                            if abs(old) not in curve_ids:
                                raise ValueError(f'Material {mid}: undefined FUNCT {old}')
                            line = replace_field(line, j*10, 10, curve_ids[abs(old)] * (-1 if old < 0 else 1))
                    lines[i] = line
                if matyp == 1 and row == 3:
                    law = line[10:20].strip().upper()
            elif card == 'FUNCT /' and row == 0:
                lines[i] = replace_field(line, 8, 8, curve_ids[numeric(line[8:16], integer=True)])
        return '\n'.join(lines).rstrip() + '\n'

    def _render_lsdyna(self, template, material, mid):
        lines, remap, keyword, row = template.splitlines(), {}, '', -1
        # Curves and tables share an ID pool; allocate all dependencies first.
        for line in lines:
            if line.lstrip().startswith('$'):
                continue
            if line.startswith('*'):
                keyword, row = line.upper().strip(), -1 if line.upper().strip().endswith('_TITLE') else 0
            elif keyword.startswith(('*DEFINE_CURVE', '*DEFINE_TABLE')):
                if row == 0:
                    old = numeric(fields(line)[0], integer=True)
                    if old in remap:
                        raise ValueError(f'Duplicate curve/table {old} in material template')
                    remap[old] = self.allocate()
                row += 1

        def ref(line, column, width=10):
            raw = fields(line, (width,)*max(8, column+1))[column]
            old = numeric(raw, integer=True)
            if not old:
                return line
            if abs(old) not in remap:
                raise ValueError(f'Material {mid}: undefined curve/table {old}')
            return replace_field(line, column*width, width, remap[abs(old)] * (-1 if old < 0 else 1))

        keyword, row, erosion_idam = '', 0, 0
        for i, line in enumerate(lines):
            if line.lstrip().startswith('$'):
                continue
            if line.startswith('*'):
                keyword, row = line.upper().strip(), -1 if line.upper().strip().endswith('_TITLE') else 0
                continue
            base = keyword.removesuffix('_TITLE')
            if base in MATERIAL_KEYWORDS:
                if row == -1:
                    line = material.name
                elif row == 0:
                    values = ((0, mid), (1, material.rho), (3, material.e), (4, material.pr)) if base in ('*MAT_JOHNSON_COOK', '*MAT_015', '*MAT_15') else enumerate((mid, material.rho, material.e, material.pr))
                    for col, value in values:
                        line = replace_field(line, col*10, 10, value)
                elif row == 1:
                    cols = ((5,) if base == '*MAT_BARLAT_YLD2000' else
                            (2, 3) if base in ('*MAT_MODIFIED_PIECEWISE_LINEAR_PLASTICITY', '*MAT_PIECEWISE_LINEAR_PLASTICITY_LOG_INTERPOLATION') else (2, 3, 5))
                    if MATERIAL_KEYWORDS[base]:
                        for col in cols:
                            if base != '*MAT_BARLAT_YLD2000' or numeric(fields(line)[col]) < 0:
                                line = ref(line, col)
            elif base.startswith(('*DEFINE_CURVE', '*DEFINE_TABLE')):
                if row == 0:
                    line = replace_field(line, 0, 10, remap[numeric(fields(line)[0], integer=True)])
                elif row > 0 and base.startswith('*DEFINE_TABLE') and line.strip():
                    line = ref(line, 1, 20)
            elif base == '*MAT_ADD_EROSION':
                if row == 0:
                    erosion_idam = 0
                    line = replace_field(line, 0, 10, mid)
                elif row == 2:
                    erosion_idam = numeric(fields(line)[0], integer=True)
                    for col in (2, 3, 7):
                        # Positive ECRIT is a scalar, negative ECRIT a curve ID.
                        if col != 3 or numeric(fields(line)[col]) < 0:
                            line = ref(line, col)
                elif row == 3 and erosion_idam:
                    line = ref(line, 3)
                elif row == (4 if erosion_idam else 3):
                    for col in (0, 5, 6, 7):
                        line = ref(line, col)
            elif base == '*MAT_ADD_DAMAGE_GISSMO':
                if row == 0:
                    line = replace_field(line, 0, 10, mid)
                elif row == 1:
                    for col in (0, 1, 5):
                        if col != 1 or numeric(fields(line)[col]) < 0:
                            line = ref(line, col)
                elif row == 2:
                    line = ref(line, 3)
            lines[i] = line
            row += 1
        # HyperMesh metadata embeds the original IDs; retaining it after ID
        # allocation would reintroduce stale entity associations on import.
        return '\n'.join(line for line in lines if not line.startswith(('$HMNAME', '$HWCOLOR', '$HMCURVE'))).rstrip() + '\n'


def require_density(material, solver):
    if material.rho is None or not math.isfinite(material.rho) or material.rho <= 0:
        from utilities.source_location import diagnostic
        raise ValueError(diagnostic(
            f'Material {material.name}: a positive density is required for {solver} output. '
            'Abaqus static models may legally omit *DENSITY, but this target conversion requires it. '
            'Add *DENSITY to the source material in consistent model units; '
            'density will not be guessed or supplied by the material JSON.', material))


def elastic_material(material, mid, solver, solid=False):
    if solver == 'abaqus':
        density = f'*DENSITY\n{material.rho}, 0.0\n' if material.rho is not None else ''
        return (f'*MATERIAL, NAME={material.name}\n' + density +
                f'*ELASTIC, TYPE=ISOTROPIC\n{material.e}, {material.pr}, 0.0\n')
    require_density(material, solver)
    if solver == 'lsdyna' and material.tag == 'rigid':
        return ('*MAT_RIGID_TITLE\n' + material.name + '\n' +
                ''.join(field(v, 10) for v in (mid, material.rho, material.e, material.pr)) + '\n' +
                ''.join(field(getattr(material, key, 0), 10) for key in ('cmo', 'con1', 'con2')) + '\n' +
                ''.join(field(0, 10) for _ in range(6)) + '\n')
    if solver == 'lsdyna':
        return ('*MAT_ELASTIC_TITLE\n' + material.name + '\n' +
                ''.join(field(v, 10) for v in (mid, material.rho, material.e, material.pr)) + '\n')
    header = 'MATER / ' + field(mid) + field(1 if solid else 100) + field(material.rho, 16) + '       0'*4 + '\n'
    header += '                                                             1.0\nNAME ' + material.name + '\n'
    if solid:
        g, k = material.e/(2*(1+material.pr)), material.e/(3*(1-2*material.pr))
        return header + field(g, 10) + '     999.0       0.0\n' + field(k, 10) + '\n\n\n' + ' '*60 + '       0.0       0.0\n\n'
    return header + field(material.e, 10) + ' '*10 + field(material.pr, 10) + '\n' + '                              \n'*5
