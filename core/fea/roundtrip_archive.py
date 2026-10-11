"""Carry source decks as checked solver comments for reversible conversions.

An unchanged generated deck can restore its archived source exactly. Edited
decks are converted normally so restoring an archive never discards user edits.
Includes are expanded before archiving; no external file is needed on return.
"""
import base64
import gzip
import hashlib
import json

MARKER = 'CIRCLECIRCLE2_ARCHIVE_V1'
GROUP_MARKER = 'CIRCLECIRCLE2_ARCHIVE_V2'
MAX_SIZE = 256 * 1024 * 1024


def digest(text):
    return hashlib.sha256(text.replace('\r\n', '\n').encode('utf-8')).hexdigest()


def split_archive(text):
    body, encoded, groups = [], [], {}
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        prefix = '** ' if stripped.startswith('** ') else '$ '
        if stripped.startswith(prefix + GROUP_MARKER + ' '):
            group, chunk = stripped[len(prefix + GROUP_MARKER + ' '):].strip().split(' ', 1)
            groups.setdefault(group, []).append(chunk)
        elif stripped.startswith(prefix + MARKER + ' '):
            encoded.append(stripped[len(prefix + MARKER + ' '):].strip())
        else:
            body.append(line)
    clean = ''.join(body)
    if not encoded and not groups:
        return clean, {}, True
    try:
        import io
        sources, unchanged = {}, False
        chunks = ([encoded] if encoded else []) + list(groups.values())
        for encoded_group in chunks:
            packed = base64.b64decode(''.join(encoded_group), validate=True)
            with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
                unpacked = stream.read(MAX_SIZE + 1)
            if len(unpacked) > MAX_SIZE:
                raise ValueError('Archive exceeds the supported source size')
            payload = json.loads(unpacked)
            current = payload['sources']
            if not isinstance(current, dict) or any(k not in ('lsdyna', 'abaqus', 'pamcrash') or
                                                   not isinstance(v, str) for k, v in current.items()):
                raise ValueError('Invalid source archive')
            for solver, source in current.items():
                if solver in sources and sources[solver] != source:
                    raise ValueError('Conflicting source archives')
                sources[solver] = source
            unchanged |= payload['body_sha256'] == digest(clean)
        return clean, sources, unchanged
    except (ValueError, KeyError, TypeError, OSError, EOFError) as error:
        raise ValueError(f'Invalid {MARKER} comments: {error}') from error


def comments(body, sources, solver):
    payload = json.dumps({'body_sha256': digest(body), 'sources': sources}, ensure_ascii=False).encode('utf-8')
    encoded = base64.b64encode(gzip.compress(payload)).decode('ascii')
    prefix = '**' if solver == 'abaqus' else '$'
    group = hashlib.sha256(payload).hexdigest()[:24]
    return ''.join(f'{prefix} {GROUP_MARKER} {group} {encoded[i:i+68]}\n' for i in range(0, len(encoded), 68))
