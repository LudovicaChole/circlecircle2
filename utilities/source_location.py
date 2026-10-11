"""Source-file locations shared by parsers and user-facing diagnostics."""
from contextlib import contextmanager
from contextvars import ContextVar

_current_source = ContextVar('fea_source', default=None)


def source_location(path=None, line=None, keyword=None):
    parts = [str(path)] if path else []
    if line:
        parts.append(f'LINE - {line}')
    if keyword:
        parts.append(str(keyword))
    return ': '.join(parts) or None


def diagnostic(message, source=None):
    message = str(message)
    if ': LINE - ' in message:
        return message
    location = getattr(source, 'source_context', None) or (source if isinstance(source, str) else None)
    location = location or _current_source.get()
    if not location or message.startswith(f'{location}: '):
        return message
    return f'{location}: {message}'


@contextmanager
def source_scope(location):
    token = _current_source.set(location)
    try:
        yield
    finally:
        _current_source.reset(token)


class SourceStore(dict):
    """Keep the location of a parsed record when it enters model storage."""
    def __setitem__(self, key, value):
        location = _current_source.get()
        if location and hasattr(value, '__dict__') and not getattr(value, 'source_context', None):
            value.source_context = location
        super().__setitem__(key, value)


def parse_source(parser, line, version, path, line_number, keyword):
    location = source_location(path, line_number, keyword)
    parser.source_context = location
    with source_scope(location):
        parser.parse(line_raw=line, version=version)
