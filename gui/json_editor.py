"""JSON highlighting and whitespace formatting without changing numeric values."""
import json
import re
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor

TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|[^\s]')


def format_json(text):
    json.loads(text)  # Validate before touching the editor.
    tokens = TOKENS.findall(text)
    result, depth = [], 0
    for index, token in enumerate(tokens):
        previous = tokens[index - 1] if index else ''
        following = tokens[index + 1] if index + 1 < len(tokens) else ''
        if token in ('{', '['):
            result.append(token)
            depth += 1
            if following not in ('}', ']'):
                result.append('\n' + '    ' * depth)
        elif token in ('}', ']'):
            depth -= 1
            if previous not in ('{', '['):
                result.append('\n' + '    ' * depth)
            result.append(token)
        elif token == ',':
            result.append(',\n' + '    ' * depth)
        elif token == ':':
            result.append(': ')
        else:
            result.append(token)
    return ''.join(result) + '\n'


class JsonHighlighter(QSyntaxHighlighter):
    pattern = re.compile(r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\b(?:true|false|null)\b')

    def highlightBlock(self, text):
        for match in self.pattern.finditer(text):
            value = match.group()
            color = '#0369a1' if value.startswith('"') and text[match.end():].lstrip().startswith(':') else (
                '#15803d' if value.startswith('"') else '#9333ea')
            style = QTextCharFormat()
            style.setForeground(QColor(color))
            self.setFormat(match.start(), len(value), style)
