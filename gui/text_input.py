"""Normalize typed/pasted full-width text; never rewrite loaded file contents."""
import unicodedata

PUNCTUATION = str.maketrans({'，': ',', '。': '.', '、': ',', '；': ';', '：': ':',
                           '？': '?', '！': '!', '“': '"', '”': '"', '‘': "'", '’': "'",
                           '（': '(', '）': ')', '【': '[', '】': ']', '《': '<', '》': '>',
                           '…': '...', '—': '-', '·': '.', '\u3000': ' '})


def english_input(text):
    result = []
    for char in text.translate(PUNCTUATION):
        code = ord(char)
        if 0xFF01 <= code <= 0xFF5E:
            char = chr(code - 0xFEE0)
        name = unicodedata.name(char, '')
        if name.startswith(('CJK UNIFIED IDEOGRAPH', 'CJK COMPATIBILITY IDEOGRAPH', 'BOPOMOFO')):
            continue
        result.append(char)
    return ''.join(result)
