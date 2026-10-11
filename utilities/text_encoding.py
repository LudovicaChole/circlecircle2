"""Lossless Unicode/legacy Western text decoding for the editor."""
import codecs


def read_solver_text(path):
    """Decode an already in-memory solver deck without a second disk read.

    Same lossless BOM/UTF-8/cp1252/latin-1 policy as detect_encoding.
    The streaming detector remains available for the interactive editor.
    """
    with open(path, 'rb') as stream:
        data = stream.read()
    for bom, encoding in ((codecs.BOM_UTF32_LE, 'utf-32-le'),
                          (codecs.BOM_UTF32_BE, 'utf-32-be'),
                          (codecs.BOM_UTF8, 'utf-8-sig'),
                          (codecs.BOM_UTF16_LE, 'utf-16-le'),
                          (codecs.BOM_UTF16_BE, 'utf-16-be')):
        if data.startswith(bom):
            return data.decode(encoding).removeprefix('\ufeff')
    for encoding in ('utf-8', 'cp1252', 'latin-1'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue


def detect_encoding(path, cancelled=None):
    # Validate the whole stream before displaying it: a non-UTF8 comment can
    # occur after many megabytes of ASCII solver cards. Memory stays bounded.
    with open(path, 'rb') as stream:
        prefix = stream.read(4)
        for bom, encoding in ((codecs.BOM_UTF32_LE, 'utf-32-le'),
                              (codecs.BOM_UTF32_BE, 'utf-32-be'),
                              (codecs.BOM_UTF8, 'utf-8-sig'),
                              (codecs.BOM_UTF16_LE, 'utf-16-le'),
                              (codecs.BOM_UTF16_BE, 'utf-16-be')):
            if prefix.startswith(bom):
                return encoding
        stream.seek(0)
        utf8 = codecs.getincrementaldecoder('utf-8')()
        valid_utf8, valid_windows = True, True
        while True:
            if cancelled is not None and cancelled.is_set():
                return 'utf-8'
            block = stream.read(65536)
            if valid_utf8:
                try:
                    utf8.decode(block, final=not block)
                except UnicodeDecodeError:
                    valid_utf8 = False
            if valid_windows:
                try:
                    block.decode('cp1252')
                except UnicodeDecodeError:
                    valid_windows = False
            if not block:
                break
        # These are reversible fallbacks, not a claim that arbitrary legacy
        # encodings can be identified unambiguously. Never discard bytes.
        return 'utf-8' if valid_utf8 else ('cp1252' if valid_windows else 'latin-1')
