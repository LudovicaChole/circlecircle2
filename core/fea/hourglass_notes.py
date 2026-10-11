"""Versioned Abaqus comments preserving source hourglass controls and mesh bindings."""
import base64
import json
import zlib
from core.fea.material_cards import pam_blocks

PREFIX = '** CIRCLECIRCLE2_HOURGLASS '


def capture(df, text, solver):
    if solver not in ('lsdyna', 'pamcrash'):
        return
    definitions, part_refs, material_controls = {}, {}, {}
    if solver == 'pamcrash':
        current = []
        for line in text.splitlines():
            if line.startswith('NUMPAR/'):
                current = [line]
            elif current:
                current.append(line)
                if line.strip() == 'END_NUMPAR':
                    definitions[int(current[0][8:16])] = '\n'.join(current) + '\n'
                    current = []
            if line.startswith('PART  /'):
                part_refs[int(line[8:16])] = int(line[56:64].strip() or '0')
        for key, rows in pam_blocks(text):
            if key == 'MATER /':
                material_controls[int(rows[0][8:16])] = {
                    'ishg': int(rows[0][48:56].strip() or '0'),
                    'qvm': rows[1][56:64].strip() if len(rows) > 1 else ''}
    global_control = next(iter(df.control_hourglass.values()), None) if solver == 'lsdyna' else None
    records = []
    for part in df.part.values():
        elements = sorted(e.uid for e in df.storge_part_element.get(part.uid, ()))
        if not elements:
            continue
        control = None
        if solver == 'lsdyna' and part.hgid in df.hourglass:
            h = df.hourglass[part.hgid]
            control = {key: getattr(h, key) for key in
                       ('uid', 'ihq', 'qm', 'ibq', 'q1', 'q2', 'qb', 'qw', 'name')}
        elif solver == 'lsdyna' and global_control is not None:
            control = {'uid': 0, 'ihq': global_control.ihq, 'qh': global_control.qh}
        elif solver == 'pamcrash':
            uid = part_refs.get(part.uid, 0)
            if uid and uid not in definitions:
                raise ValueError(f'Part {part.uid}: missing PAM NUMPAR {uid}')
            control = dict(material_controls.get(part.mid, {}),
                           uid=uid, numpar=definitions.get(uid))
        if control is not None:
            records.append({'elements': elements, 'control': control})
    if records:
        df.storge['hourglass_notes']['source'] = {'version': 1, 'solver': solver, 'parts': records}


def write_comments(df):
    notes = df.storge['hourglass_notes'].get('source')
    if not notes:
        return []
    packed = base64.b64encode(zlib.compress(json.dumps(notes, separators=(',', ':')).encode())).decode()
    readable = ['** HOURGLASS CONTROLS: preserved ' + notes['solver'] + ' settings for reverse conversion.\n']
    seen = set()
    for item in notes['parts']:
        control = item['control']
        summary = (('HGID=' + str(control['uid']) + ' ' + ' '.join(
                    key.upper() + '=' + str(value) for key, value in control.items()
                    if key not in ('uid', 'name'))) if notes['solver'] == 'lsdyna' else
                   'IDNUMPAR=' + str(control['uid']) + ' ISHG=' + str(control.get('ishg', 0)))
        if summary not in seen:
            readable.append('** HOURGLASS ' + summary + '\n')
            seen.add(summary)
    return readable + [PREFIX + packed[i:i+160] + '\n' for i in range(0, len(packed), 160)]


def restore(df, text, target):
    chunks = [line[len(PREFIX):].strip() for line in text.splitlines() if line.startswith(PREFIX)]
    if not chunks:
        return
    try:
        notes = json.loads(zlib.decompress(base64.b64decode(''.join(chunks), validate=True)))
        if notes['version'] != 1 or notes['solver'] not in ('lsdyna', 'pamcrash'):
            raise ValueError('Unsupported hourglass note version or solver')
        records = [(set(item['elements']), item['control']) for item in notes['parts']]
    except (ValueError, KeyError, TypeError, zlib.error) as error:
        raise ValueError(f'Invalid CIRCLECIRCLE2_HOURGLASS comments: {error}') from error
    df.storge['hourglass_notes']['source'] = notes
    if target != notes['solver']:
        return
    for part in df.part.values():
        elements = {e.uid for e in df.storge_part_element.get(part.uid, ())}
        matching = [control for original, control in records if elements and elements <= original]
        if len(matching) > 1:
            raise ValueError(f'Part {part.uid}: ambiguous hourglass note association')
        if matching:
            control = matching[0]
            if target == 'lsdyna':
                from core.fea.model.lsdyna.hourglass import Hourglass
                uid = control['uid']
                if not uid:
                    from types import SimpleNamespace
                    df.control_hourglass[1] = SimpleNamespace(uid=1, ihq=control['ihq'], qh=control['qh'])
                    part.hourglass_from_global = True
                    continue
                if uid in df.hourglass and any(getattr(df.hourglass[uid], key) != value for key, value in control.items()):
                    raise ValueError(f'Conflicting hourglass note ID {uid}')
                df.hourglass[uid] = Hourglass(**control)
                part.hgid = uid
            else:
                df.storge['hourglass_notes'][part.uid] = control


def restore_pam_material(df, text, mid):
    controls = [df.storge['hourglass_notes'][p.uid] for p in df.part.values()
                if p.mid == mid and p.uid in df.storge['hourglass_notes']]
    if not controls:
        return text
    settings = {(c.get('ishg', 0), c.get('qvm', '')) for c in controls}
    if len(settings) != 1:
        raise ValueError(f'Material {mid}: conflicting restored PAM hourglass settings')
    ishg, qvm = settings.pop()
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('MATER /'):
            lines[i] = line.ljust(72)[:48] + str(ishg).rjust(8) + line.ljust(72)[56:]
            if qvm:
                value = lines[i+1].ljust(64)
                lines[i+1] = value[:56] + qvm.rjust(8) + value[64:]
    return '\n'.join(lines) + '\n'

