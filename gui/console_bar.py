"""An immutable console transcript and a separate editable command prompt."""
import logging
import platform
from datetime import datetime
from PySide6.QtGui import QTextCursor, QTextCharFormat, QTextBlockFormat, QColor, QFont
from PySide6.QtCore import QObject, Signal, Slot, Qt
from PySide6.QtWidgets import QWidget, QTextEdit, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout


class LogBridge(QObject):
    message = Signal(str, int)


class ConsoleLogHandler(logging.Handler):
    def __init__(self, console):
        super().__init__(logging.INFO)
        self.bridge = LogBridge(console)
        self.bridge.message.connect(console.append_record, Qt.QueuedConnection)
        self.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

    def emit(self, record):
        try:
            self.bridge.message.emit(self.format(record), record.levelno)
        except RuntimeError:
            pass  # The receiving window has already closed.
        except Exception:
            self.handleError(record)


class CommandInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self.history_position = 0
        self.draft = ''

    def remember(self, command):
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_position = len(self.history)
        self.draft = ''

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            if self.history_position == len(self.history):
                self.draft = self.text()
            step = -1 if event.key() == Qt.Key_Up else 1
            self.history_position = max(0, min(len(self.history), self.history_position + step))
            self.setText(self.history[self.history_position]
                         if self.history_position < len(self.history) else self.draft)
            return
        super().keyPressEvent(event)


class C2Console(QWidget):
    commandEntered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.prompt = '> '
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.history = QTextEdit(self)
        self.history.setAcceptRichText(False)
        self.history.setReadOnly(True)
        self.history.setUndoRedoEnabled(False)
        self.history.setAcceptDrops(False)
        self.history.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.history.document().setMaximumBlockCount(10000)
        self.history.setStyleSheet('''
            QTextEdit { font-family: Consolas; font-size: 13px; background: #f8fafc; padding: 8px; }
            QScrollBar:vertical { background: #f1f5f9; width: 12px; margin: 0; }
            QScrollBar::handle:vertical { background: #b8c4d2; min-height: 28px;
                                         border-radius: 4px; margin: 0 2px; }
            QScrollBar::handle:vertical:hover { background: #94a3b8; }
            QScrollBar::handle:vertical:pressed { background: #7d8da3; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: #f1f5f9; }
        ''')
        layout.addWidget(self.history)
        row = QHBoxLayout()
        row.addWidget(QLabel(self.prompt))
        self.input = CommandInput(self)
        self.input.setPlaceholderText('Enter command… (-help)')
        self.input.returnPressed.connect(self.submit_command)
        row.addWidget(self.input)
        layout.addLayout(row)
        self.setFocusProxy(self.input)
        self.append_message(f'CircleCircle2 Console 1.0\nPython {platform.python_version()}\n'
                            'Type -help for more information.\n')

    @Slot(str)
    def append_message(self, message):
        self.append_record(str(message), logging.INFO)

    @Slot(str, int)
    def append_record(self, message, level):
        error = level >= logging.ERROR
        warning = level >= logging.WARNING
        foreground = '#b42318' if error else '#92400e' if warning else '#253449'
        background = '#fff0ef' if error else '#fff8e6' if warning else '#ffffff'
        self._append_block(str(message).rstrip('\n'), foreground, background, bold=error)

    def _append_block(self, text, foreground, background, bold=False):
        scrollbar = self.history.verticalScrollBar()
        follow = scrollbar.value() >= scrollbar.maximum() - 3
        cursor = QTextCursor(self.history.document())
        cursor.movePosition(QTextCursor.End)
        block = QTextBlockFormat()
        block.setTopMargin(7)
        block.setBottomMargin(7)
        block.setLeftMargin(8)
        block.setRightMargin(8)
        block.setBackground(QColor(background))
        char = QTextCharFormat()
        char.setForeground(QColor(foreground))
        char.setFontWeight(QFont.Bold if bold else QFont.Normal)
        if not self.history.document().isEmpty():
            cursor.insertBlock(block, char)
        else:
            cursor.setBlockFormat(block)
        # Soft line breaks keep a multiline message inside one visual group.
        cursor.insertText(text.replace('\r\n', '\n').replace('\n', '\u2028'), char)
        if follow:
            scrollbar.setValue(scrollbar.maximum())

    def begin_operation(self, title):
        self._append_block(f'── {datetime.now():%H:%M:%S}  {title} ──', '#1e40af', '#dbeafe', True)

    def toPlainText(self):
        return self.history.toPlainText()

    def submit_command(self):
        command = self.input.text().strip()
        if not command:
            return
        self.begin_operation('COMMAND')
        self._append_block(self.prompt + command, '#1e40af', '#eff6ff', True)
        self.input.remember(command)
        self.input.clear()
        self.commandEntered.emit(command)
