"""FEA cleanup preferences and preview; never follow directory links."""
import json
import os
import stat
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
                               QPlainTextEdit, QDialogButtonBox, QLabel, QFrame)
from utilities.error_messages import error_message
from utilities.app_paths import config_directory
from utilities.licensing import atomic_write

DEFAULT_KEEP = ('.inp', '.geo', '.k', '.key', '.pc', '.inc', '.jpg', '.png', '.gif', '.mp4', '.avi', '.md')
DEFAULT_NAMES = ('binout',)


def keep_names():
    path = config_directory() / 'clear_fea_result.json'
    data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if not isinstance(data, dict):
        raise ValueError('Invalid Clear FEA Result configuration.')
    values = data.get('keep_names', list(DEFAULT_NAMES))
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError('Preserved filenames must be a list of strings.')
    return normalize_names(','.join(values))


def normalize_names(text):
    names = sorted(set(text.replace(';', ',').replace('\n', ',').split(',')))
    names = [name.strip().lower() for name in names if name.strip()]
    if any('.' in n or any(c in n for c in '/\\:*?<>|"') for n in names):
        raise ValueError('Enter exact extensionless filenames, such as binout.')
    return sorted(set(names))


def is_link(path):
    return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0)
                                    & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0))


def normalize_extensions(text):
    extensions = []
    for item in text.replace(';', ',').replace('\n', ',').replace(' ', ',').split(','):
        item = item.strip().lower().lstrip('*')
        if not item:
            continue
        item = item if item.startswith('.') else '.' + item
        if len(item) < 2 or any(c in item for c in '/\\:*?<>|"'):
            raise ValueError('Enter file extensions such as .inp, .k, .png.')
        extensions.append(item)
    if not extensions:
        raise ValueError('At least one extension must be preserved.')
    return sorted(set(extensions))


def keep_extensions():
    path = config_directory() / 'clear_fea_result.json'
    if not path.exists():
        return DEFAULT_KEEP
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('Invalid Clear FEA Result configuration.')
    values = data['keep_extensions']
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ValueError('Invalid Clear FEA Resault configuration.')
    return normalize_extensions(','.join(values))


def configure(parent):
    try:
        dialog = QDialog(parent)
        dialog.setWindowTitle('Clear FEA Result')
        dialog.resize(640, 480)
        dialog.setStyleSheet('''
            QDialog { background: #f8fafc; }
            QFrame#RulePanel { background: white; border: 1px solid #cbd5e1; border-radius: 8px; }
            QLabel#RuleTitle { color: #1e293b; font-weight: 600; }
            QLabel#RuleHint { color: #64748b; }
            QPlainTextEdit { background: white; border: 1px solid #e2e8f0;
                             border-radius: 6px; padding: 8px; }
            QPlainTextEdit:focus { border-color: #60a5fa; }
            QPushButton { min-width: 76px; min-height: 30px; padding: 2px 12px; }
        ''')
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        introduction = QLabel('Choose which files to keep during FEA result cleanup.')
        introduction.setWordWrap(True)
        introduction.setAlignment(Qt.AlignCenter)
        layout.addWidget(introduction)
        extensions = QPlainTextEdit('\n'.join(keep_extensions()))
        names = QPlainTextEdit('\n'.join(keep_names()))
        panels = QHBoxLayout()
        panels.setSpacing(16)
        for title, hint, editor, placeholder in (
            ('Preserve extensions', 'One per line · Include the leading dot', extensions, '.inp\n.geo\n.md'),
            ('Preserve filenames', 'One per line · Exact names without extensions', names, 'binout')):
            panel = QFrame()
            panel.setObjectName('RulePanel')
            column = QVBoxLayout(panel)
            column.setContentsMargins(14, 16, 14, 14)
            column.setSpacing(10)
            heading = QLabel(title)
            heading.setObjectName('RuleTitle')
            heading.setAlignment(Qt.AlignCenter)
            column.addWidget(heading)
            note = QLabel(hint)
            note.setObjectName('RuleHint')
            note.setWordWrap(True)
            note.setAlignment(Qt.AlignCenter)
            note.setMinimumHeight(36)
            column.addWidget(note)
            heading.setBuddy(editor)
            editor.setAccessibleName(title)
            editor.setPlaceholderText(placeholder)
            editor.setToolTip(hint)
            column.addWidget(editor, 1)
            panels.addWidget(panel, 1)
        layout.addLayout(panels, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        def save():
            try:
                data = {'keep_extensions': normalize_extensions(extensions.toPlainText()),
                        'keep_names': normalize_names(names.toPlainText())}
                atomic_write(config_directory() / 'clear_fea_result.json', json.dumps(data, indent=2))
                dialog.accept()
            except (OSError, ValueError) as error:
                QMessageBox.warning(dialog, 'Clear FEA Result', error_message(error))
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()
    except (OSError, ValueError, KeyError, TypeError) as error:
        QMessageBox.warning(parent, 'Clear FEA Resault', error_message(error))


def cleanup_candidates(directory, keep, names=None):
    preserved_names = set(keep_names() if names is None else names)
    root = Path(directory).resolve(strict=True)
    if is_link(Path(directory)):
        raise ValueError('Linked folders cannot be cleared.')
    files = []
    for folder, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if not is_link(Path(folder) / name)]
        for name in names:
            path = Path(folder) / name
            if not is_link(path) and path.suffix.lower() not in keep and path.name.lower() not in preserved_names:
                files.append(path)
    return files
