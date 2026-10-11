"""Shared input diagnostics; invalid data must never turn into partial output."""
from functools import wraps
from utilities.source_location import diagnostic
from inspect import signature
from core.fea.lsdyna.parser.card_fields import fields, number


class FeaInputError(ValueError):
    pass


def guarded(stage):
    def decorate(method):
        params = list(signature(method).parameters)
        version_index = params.index('version') - 1 if 'version' in params else None
        @wraps(method)
        def run(self, *args, **kwargs):
            try:
                version = kwargs.get('version')
                if version is None and version_index is not None and len(args) > version_index:
                    version = args[version_index]
                if version is not None and getattr(self, 'version', None) and version not in self.version:
                    raise ValueError(f'Unsupported version {version}')
                return method(self, *args, **kwargs)
            except FeaInputError:
                raise
            except Exception as error:
                detail = f'missing reference/key {error}' if isinstance(error, KeyError) else str(error)
                raise FeaInputError(f'{stage} {type(self).__name__}: {detail}') from error
        return run
    return decorate


def required_id(raw, name, df):
    if not str(raw).strip():
        raise FeaInputError(f'{name} is required (field is blank)')
    try:
        value = number(raw, df, integer=True)
    except (ValueError, KeyError) as error:
        raise FeaInputError(f'{name}={raw!r}: invalid integer or undefined parameter') from error
    if value <= 0:
        raise FeaInputError(f'{name} must be positive; got {value}')
    return value


def validate_card(keyword, line, parser):
    """Validate mandatory identifiers only; optional solver defaults stay legal.

    Called by the solver before every registered LS-DYNA parser. Extend this
    registry for additional card layouts; other errors still get source context.
    """
    base = keyword.removesuffix('_TITLE')
    index = parser.line_number - int(keyword.endswith('_TITLE'))
    if index < 0:
        return
    schema, widths = {}, (10,)*8
    if base == '*NODE':
        schema, widths = {0: 'NID'}, (8,16,16,16)
    elif base == '*ELEMENT_SHELL':
        schema, widths = {0:'EID',1:'PID',2:'N1',3:'N2',4:'N3'}, (8,)*10
    elif base == '*ELEMENT_SOLID':
        schema, widths = ({0:'EID',1:'PID'} if index == 0 else {i:f'N{i+1}' for i in range(8)}), (8,)*8
    elif base in ('*PART', '*PART_INERTIA') and parser.line_number == 1:
        schema = {0:'PID',1:'SECID'}
        if not fields(line)[7].strip() or not number(fields(line)[7], parser.dataframe):
            schema[2] = 'MID'
    elif base.startswith('*MAT_') and index == 0:
        schema = {0:'MID'}
    elif base.startswith('*SECTION_') and index == 0:
        schema = {0:'SECID'}
    elif base.startswith('*SET_') and index == 0:
        schema = {0:'SID'}
    elif base.startswith(('*DEFINE_CURVE', '*DEFINE_TABLE')) and index == 0:
        schema = {0:'LCID'}
    elif base == '*CONSTRAINED_NODAL_RIGID_BODY':
        schema = {0:'PID',2:'NSID'}
    values = fields(line, widths)
    for column, name in schema.items():
        required_id(values[column], name, parser.dataframe)


def finish_keyword(keyword, line_count, context, parser=None):
    """Catch truncated/empty blocks that never reach a parser's commit step."""
    base = keyword.removesuffix('_TITLE')
    minimum = 0
    if base.startswith('*EM_'):
        from core.fea.lsdyna.em_cards import EM_SCHEMAS
        if base[1:] in EM_SCHEMAS:
            minimum = EM_SCHEMAS[base[1:]].minimum
    if base in ('*PART', '*PART_INERTIA'):
        minimum = 2
    elif base.startswith(('*MAT_', '*SECTION_', '*SET_', '*DEFINE_')):
        minimum = 1 + int(keyword.endswith('_TITLE'))
    elif base.startswith(('*ELEMENT_', '*NODE', '*CONSTRAINED_')):
        minimum = 1 + int(keyword.endswith('_TITLE'))
    required_cards = {'*MAT_ADD_EROSION': 2, '*INITIAL_VELOCITY': 2, '*MAT_RIGID': 3, '*SECTION_SHELL': 2, '*SECTION_BEAM': 2,
                      '*DEFINE_CURVE': 2, '*DEFINE_TABLE': 2, '*DEFINE_TABLE_2D': 2}
    if base in required_cards:
        minimum = required_cards[base] + int(keyword.endswith('_TITLE'))
    if line_count < minimum:
        raise FeaInputError(f'{context}: incomplete {keyword}: expected at least {minimum} data lines, got {line_count}')
    if base == '*MAT_ADD_EROSION' and parser is not None and getattr(getattr(parser, 'current_material', None), 'idam', 0) == 1 and line_count < 4+int(keyword.endswith('_TITLE')):
        raise FeaInputError(f'{context}: incomplete MAT_ADD_EROSION GISSMO cards')
    if base == '*ELEMENT_SOLID' and (parser.line_number if parser is not None else line_count % 2):
        raise FeaInputError(f'{context}: incomplete *ELEMENT_SOLID: missing connectivity line')
    if base == '*ELEMENT_BEAM_ORIENTATION' and parser is not None and parser.temp:
        raise FeaInputError(f'{context}: incomplete *ELEMENT_BEAM_ORIENTATION: missing orientation vector')
    if parser is not None and getattr(parser, 'cards', 1) > 1 and parser.temp:
        raise FeaInputError(f'{context}: incomplete {keyword}: missing continuation card')
    if base in ('*BOUNDARY_SPC_NODE_ID', '*BOUNDARY_SPC_SET_ID') and line_count % 2:
        raise FeaInputError(f'{context}: incomplete {keyword}: missing constraint card')


def validate_references(df):
    """Check shared model dependencies before any target writer runs."""
    for motion in df.storge['prescribed_motion_node'].values():
        if motion.nid not in df.node or motion.lcid not in df.define_curve:
            raise FeaInputError(f'Prescribed motion {motion.uid}: missing node or curve')
    duplicate_elements = df.element_shell.keys() & df.element_solid.keys()
    if duplicate_elements:
        raise FeaInputError(f'Duplicate shell/solid element identifiers: {sorted(duplicate_elements)}')
    duplicates = df.storge['element_beam'].keys() & (df.element_shell.keys() | df.element_solid.keys())
    if duplicates:
        raise FeaInputError(f'Duplicate beam/shell/solid identifiers: {sorted(duplicates)}')
    for family in ('boundary_spc_node', 'initial_velocity_node'):
        for nid, obj in df.storge[family].items():
            if nid not in df.node:
                raise FeaInputError(diagnostic(f'{family}: missing node {nid}', obj))
    for pid, part in df.part.items():
        thermal_only = any(getattr(c, 'soln', 0) == 1 for c in df.control_solution.values())
        if not thermal_only and part.mid not in df.material:
            raise FeaInputError(diagnostic(f'*PART PID={pid}: MID={part.mid} references a missing material', part))
        if part.secid not in df.section_shell and part.secid not in df.section_solid and part.secid not in df.section_beam:
            raise FeaInputError(diagnostic(f'*PART PID={pid}: SECID={part.secid} references a missing section', part))
    if not any(getattr(c, 'soln', 0) in (1, 2) for c in df.control_solution.values()):
        used_sections = {df.part[e.pid].secid for e in df.element_shell.values() if e.pid in df.part}
        for sid in used_sections:
            section = df.section_shell.get(sid)
            if section is None:
                continue
            if section.elform in (12, 13, 14, 15):
                raise FeaInputError(diagnostic(
                    f'SECTION_SHELL {sid}: structural planar/axisymmetric ELFORM={section.elform} '
                    'is not mapped; cannot replace it with a 3D shell', section))
            if len({section.t1, section.t2, section.t3, section.t4}) != 1:
                raise FeaInputError(diagnostic(
                    f'SECTION_SHELL {sid}: varying nodal thickness is not mapped; '
                    'cannot use T1 as a uniform thickness', section))
    for name in ('element_shell', 'element_solid', 'element_beam'):
        for eid, element in df.storge[name].items():
            if element.pid not in df.part:
                raise FeaInputError(diagnostic(f'*{name.upper()} EID={eid}: PID={element.pid} references a missing part', element))
            for column in range(1, {'element_solid': 9, 'element_shell': 5, 'element_beam': 4}[name]):
                nid = getattr(element, f'n{column}')
                if nid and nid not in df.node:
                    raise FeaInputError(diagnostic(f'*{name.upper()} EID={eid}: N{column}={nid} references a missing node', element))
    for extra in df.constrained_extra_nodes_set.values():
        label = f'{getattr(extra, "source_context", "*CONSTRAINED_EXTRA_NODES_SET")} PID={extra.pid} NSID={extra.nsid}'
        if extra.pid not in df.part:
            raise FeaInputError(f'{label}: missing part')
        if df.material[df.part[extra.pid].mid].tag != 'rigid':
            raise FeaInputError(f'{label}: target part must use MAT20')
        if extra.nsid not in df.set_node_list:
            raise FeaInputError(f'{label}: missing node set')
    for sid, group in df.set_node_list.items():
        for raw in group.ids:
            nid = number(raw, df, integer=True)
            if nid and nid not in df.node:
                raise FeaInputError(diagnostic(f'*SET_NODE_LIST SID={sid}: NID={nid} references a missing node', group))
