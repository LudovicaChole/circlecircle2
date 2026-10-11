"""Progressive text loading with bounded GUI work and protected input."""
import os
from pathlib import Path
from threading import Event
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QTextCursor, QTextDocument, QShortcut, QKeySequence, QInputMethodEvent, QKeyEvent, QFontDatabase
from gui.file_types import TEXT_EXTENSIONS, MEDIA_EXTENSIONS
from gui.markdown_preview import MarkdownHighlighter
from gui.json_editor import JsonHighlighter, format_json
from gui.solver_editor import (SolverHighlighter as DynaHighlighter, SolverRuler as DynaRuler,
                               SolverGutter as DynaGutter, paint_field_guides, solver_for_file)
from gui.text_input import english_input
from utilities.error_messages import error_message
from utilities.logger import logger
from utilities.text_encoding import detect_encoding


class FileLoaderThread(QThread):
    chunk_ready = Signal(str, int, int)
    finished_loading = Signal()
    failed = Signal(str)

    def __init__(self, filepath, chunk_size=65536, encoding=None):
        super().__init__()
        self.filepath, self.chunk_size, self.encoding = filepath, chunk_size, encoding
        self.cancelled, self.consumed = Event(), Event()
        self.newline = None
        self.bom = ''

    def run(self):
        try:
            self.encoding = self.encoding or detect_encoding(self.filepath, self.cancelled)
            if self.cancelled.is_set():
                return
            with open(self.filepath, 'r', encoding=self.encoding) as stream:
                total = os.fstat(stream.fileno()).st_size
                first = True
                while not self.cancelled.is_set():
                    text = stream.read(16384 if first else self.chunk_size)
                    if first and self.encoding in ('utf-16-le', 'utf-16-be', 'utf-32-le', 'utf-32-be') and text.startswith('\ufeff'):
                        self.bom, text = '\ufeff', text[1:]
                    if isinstance(stream.newlines, str):
                        self.newline = stream.newlines
                    if not text and not first:
                        break
                    first = False
                    self.consumed.clear()
                    if self.cancelled.is_set():
                        break
                    self.chunk_ready.emit(text, stream.tell(), total)
                    # At most one unconsumed chunk, so Qt never accumulates a backlog.
                    self.consumed.wait()
                    if not text:
                        break
        except Exception as error:
            if not self.cancelled.is_set():
                self.failed.emit(error_message(error))
        finally:
            self.finished_loading.emit()

    def stop(self):
        self.cancelled.set()
        self.consumed.set()


class C2TextEditor(QPlainTextEdit):
    stateChanged = Signal()
    openRequested = Signal(str)
    mediaRequested = Signal(str)
    markdownRequested = Signal()
    dropFile = Signal(str)
    newFile = Signal()
    saveFile = Signal()
    openFile = Signal()

    @property
    def current_file(self):
        return getattr(self, '_current_file', None)

    @current_file.setter
    def current_file(self, value):
        self._current_file = value
        self.stateChanged.emit()

    @property
    def is_loading(self):
        return getattr(self, '_is_loading', False)

    @is_loading.setter
    def is_loading(self, value):
        self._is_loading = value
        self.stateChanged.emit()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setAttribute(Qt.WA_InputMethodEnabled, False)
        self.current_file = self.loader_thread = self._pending = self._highlighter = None
        self.is_loading = False
        self._workers = set()
        self.file_encoding, self.file_newline = 'utf-8', None
        self.file_bom = ''
        self.append_timer = QTimer(self)
        self.append_timer.setTimerType(Qt.PreciseTimer)
        self.append_timer.setSingleShot(True)
        self.append_timer.timeout.connect(self.consume_pending)
        self.setup_search_panel()
        self.load_label = QLabel(self)
        self.load_label.setStyleSheet('background: #e0f2fe; color: #075985; padding: 5px;')
        self.load_label.hide()
        self.markdown_button = QPushButton('Markdown Preview', self)
        self.markdown_button.clicked.connect(self.markdownRequested.emit)
        self.markdown_button.hide()
        self._normal_font = self.font()
        self.apply_preferences()
        self._dyna_highlighter = None
        self.dyna_ruler = DynaRuler(self)
        self.dyna_gutter = DynaGutter(self)
        self.dyna_ruler.hide()
        self.dyna_gutter.hide()
        self.cursorPositionChanged.connect(self.refresh_dyna_guides)
        self.updateRequest.connect(self.refresh_dyna_guides)
        self.blockCountChanged.connect(self.update_insets)

    def apply_preferences(self, values=None):
        from utilities.profile_settings import ProfileSettings
        values = values or ProfileSettings().preferences()
        self._font_size = values['font_size']
        self._normal_font.setPointSize(self._font_size)
        font = self.font()
        font.setPointSize(self._font_size)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth if values['word_wrap'] else QPlainTextEdit.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance('0') * 4)
        if hasattr(self, 'dyna_ruler'):
            self.update_insets()
            self.refresh_dyna_guides()

    @property
    def dyna_mode(self):
        return self.solver_mode == 'lsdyna'

    @property
    def solver_mode(self):
        return self._dyna_highlighter.solver if self._dyna_highlighter is not None else ''

    def update_dyna_mode(self, sample=None):
        if sample is None:
            block, lines = self.document().firstBlock(), []
            for _ in range(128):
                if not block.isValid():
                    break
                lines.append(block.text()[:512])
                block = block.next()
            sample = '\n'.join(lines)
        solver = solver_for_file(self.current_file, sample)
        enabled = bool(solver)
        if self._dyna_highlighter is not None and solver != self.solver_mode:
            self._dyna_highlighter.setDocument(None)
            self._dyna_highlighter.deleteLater()
            self._dyna_highlighter = None
            self.setFont(self._normal_font)
        if enabled and self._dyna_highlighter is None:
            fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
            # Windows' offscreen/default platform can return an unavailable
            # "monospace" alias. Prefer an installed fixed-pitch family.
            families = set(QFontDatabase.families())
            for family in ('Consolas', 'Cascadia Mono', 'Courier New', 'DejaVu Sans Mono'):
                if family in families:
                    fixed_font.setFamily(family)
                    break
            fixed_font.setPointSize(self._font_size)
            self.setFont(fixed_font)
            self.setTabStopDistance(self.fontMetrics().horizontalAdvance('0') * 4)
            self._dyna_highlighter = DynaHighlighter(self.document(), solver)
        elif not enabled and self._dyna_highlighter is not None:
            self._dyna_highlighter.setDocument(None)
            self._dyna_highlighter.deleteLater()
            self._dyna_highlighter = None
            self.setFont(self._normal_font)
        self.dyna_ruler.setVisible(enabled)
        self.dyna_gutter.setVisible(enabled)
        self.refresh_dyna_guides()

    def refresh_dyna_guides(self, *_):
        if hasattr(self, 'dyna_ruler') and self.solver_mode:
            self.dyna_ruler.update()
            self.dyna_gutter.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if hasattr(self, '_dyna_highlighter') and self.solver_mode and self.lineWrapMode() == QPlainTextEdit.NoWrap:
            paint_field_guides(self)

    def setup_search_panel(self):
        self.search_panel = QWidget(self)
        self.search_panel.setObjectName('SearchPanel')
        self.search_panel.setStyleSheet('''
            QWidget#SearchPanel { background: #eff6ff; border: 2px solid #2563eb; border-radius: 5px; }
            QLineEdit { background: white; color: #172554; padding: 5px; }
            QPushButton { padding: 4px; min-width: 25px; }
        ''')
        layout = QHBoxLayout(self.search_panel)
        layout.setContentsMargins(8, 6, 8, 6)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Find text — ignore case')
        self.search_input.returnPressed.connect(self.find_next)
        self.btn_prev, self.btn_next, self.btn_close = QPushButton('↑'), QPushButton('↓'), QPushButton('×')
        self.btn_prev.setToolTip('Previous match')
        self.btn_next.setToolTip('Next match')
        self.btn_prev.clicked.connect(self.find_prev)
        self.btn_next.clicked.connect(self.find_next)
        self.btn_close.clicked.connect(self.hide_search)
        self.search_status = QLabel('Ignore case')
        for widget in (self.search_input, self.btn_prev, self.btn_next, self.search_status, self.btn_close):
            layout.addWidget(widget)
        self.search_panel.hide()
        self.shortcut_find = QShortcut(QKeySequence('Ctrl+F'), self)
        self.shortcut_find.setContext(Qt.WidgetWithChildrenShortcut)
        self.shortcut_find.activated.connect(self.show_search)
        self.shortcut_esc = QShortcut(QKeySequence('Esc'), self)
        self.shortcut_esc.setContext(Qt.WidgetWithChildrenShortcut)
        self.shortcut_esc.activated.connect(self.hide_search)
        # File shortcuts are owned by the main-window menu actions.

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.position_panels()

    def position_panels(self):
        width = max(100, min(600, self.viewport().width() - 16))
        viewport = self.viewport().geometry()
        self.search_panel.setGeometry(max(0, viewport.right() - width - 8), 8, width, 52)
        if hasattr(self, 'load_label'):
            self.load_label.setGeometry(8, max(0, self.height() - 38), max(100, self.viewport().width() - 16), 28)
            y = 68 if not self.search_panel.isHidden() else 6
            self.markdown_button.setGeometry(max(0, self.viewport().width() - 170), y, 155, 28)
        if hasattr(self, 'dyna_ruler') and self.solver_mode:
            self.dyna_ruler.setGeometry(viewport.x(), viewport.y() - DynaRuler.HEIGHT,
                                       viewport.width(), DynaRuler.HEIGHT)
            self.dyna_gutter.setGeometry(1, viewport.y(), max(0, viewport.x() - 1), viewport.height())

    def update_insets(self, *_):
        # Reserve toolbar space rather than covering the text or the found match.
        top = (64 if not self.search_panel.isHidden() else 0)
        top += 36 if not self.markdown_button.isHidden() else 0
        left = 0
        if hasattr(self, '_dyna_highlighter') and self.solver_mode:
            top += DynaRuler.HEIGHT
            left = self.fontMetrics().horizontalAdvance('0') * max(4, len(str(self.blockCount()))) + 14
        self.setViewportMargins(left, top, 0, 36 if self.is_loading else 0)
        self.position_panels()

    def show_search(self):
        if self.textCursor().hasSelection():
            self.search_input.setText(self.textCursor().selectedText())
        self.position_panels()
        self.search_panel.show()
        self.update_insets()
        self.search_panel.raise_()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def hide_search(self):
        self.setExtraSelections([])
        self.search_panel.hide()
        self.update_insets()
        self.setFocus()

    def find_next(self):
        self.find_match(False)

    def find_prev(self):
        self.find_match(True)

    def find_match(self, backward):
        self.setExtraSelections([])
        text = self.search_input.text()
        if not text:
            return
        flags = QTextDocument.FindBackward if backward else QTextDocument.FindFlags()
        cursor = self.document().find(text, self.textCursor(), flags)
        wrapped = False
        if cursor.isNull():
            start = QTextCursor(self.document())
            start.movePosition(QTextCursor.End if backward else QTextCursor.Start)
            cursor = self.document().find(text, start, flags)
            wrapped = True
        if cursor.isNull():
            self.search_status.setText('No match' + (' in loaded text' if self.is_loading else ''))
        else:
            self.setTextCursor(cursor)
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            from PySide6.QtGui import QColor
            selection.format.setBackground(QColor('#ff8c00'))
            selection.format.setForeground(QColor('#111827'))
            self.setExtraSelections([selection])
            from PySide6.QtGui import QPalette
            palette = self.palette()
            for group in (QPalette.Active, QPalette.Inactive):
                palette.setColor(group, QPalette.Highlight, QColor('#ff8c00'))
                palette.setColor(group, QPalette.HighlightedText, QColor('#111827'))
            self.setPalette(palette)
            self.ensureCursorVisible()
            self.search_status.setText('Wrapped' if wrapped else 'Match')

    def keyPressEvent(self, event):
        text = event.text()
        if text and not event.modifiers() & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
            normalized = english_input(text)
            if normalized != text:
                if normalized:
                    super().keyPressEvent(QKeyEvent(event.type(), event.key(), event.modifiers(), normalized,
                                                   event.isAutoRepeat(), event.count()))
                return
        super().keyPressEvent(event)

    def inputMethodEvent(self, event):
        translated = QInputMethodEvent()
        translated.setCommitString(english_input(event.commitString()), event.replacementStart(), event.replacementLength())
        super().inputMethodEvent(translated)

    def insertFromMimeData(self, source):
        if source.hasText() and not self.isReadOnly():
            self.insertPlainText(english_input(source.text()))

    @staticmethod
    def drop_paths(mime):
        if not mime.hasUrls():
            return []
        paths = []
        for url in mime.urls():
            path = Path(url.toLocalFile())
            if not url.isLocalFile() or not path.is_file() or path.suffix.lower() not in (*TEXT_EXTENSIONS, *MEDIA_EXTENSIONS):
                return []
            paths.append(str(path))
        if sum(Path(p).suffix.lower() in TEXT_EXTENSIONS for p in paths) > 1:
            return []
        return paths

    @staticmethod
    def drop_path(mime):
        paths = C2TextEditor.drop_paths(mime)
        return paths[0] if len(paths) == 1 else None

    def dragEnterEvent(self, event):
        if self.drop_paths(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        paths = self.drop_paths(event.mimeData())
        if not paths:
            event.ignore()
            return
        for path in paths:
            if Path(path).suffix.lower() in MEDIA_EXTENSIONS:
                self.mediaRequested.emit(path)
            else:
                self.openRequested.emit(path)
        event.acceptProposedAction()

    def open_file(self, path):
        self.stop_loading()
        self._previous_file = self.current_file
        self.current_file = str(path)
        self._started = self._load_failed = False
        self.is_loading = True
        self.setReadOnly(True)
        self.load_label.setText('Opening… First text will appear while the remaining file loads.')
        self.position_panels()
        self.load_label.show()
        self.update_insets()
        self.loader_thread = FileLoaderThread(str(path))
        thread = self.loader_thread
        self._workers.add(thread)
        thread.chunk_ready.connect(self.on_chunk_ready)
        thread.failed.connect(self.on_load_failed)
        thread.finished_loading.connect(self.on_load_finished)
        thread.finished.connect(self.release_worker)
        thread.start()
        return True

    def release_worker(self):
        thread = self.sender()
        self._workers.discard(thread)
        if thread is self.loader_thread:
            self.loader_thread = None
        thread.deleteLater()

    def on_chunk_ready(self, text, loaded, total):
        thread = self.sender()
        if thread is not self.loader_thread:
            thread.consumed.set()
            return
        self._pending = (text, loaded, total, thread)
        self.append_timer.start(0 if not self._started else 1)

    def consume_pending(self):
        if self._pending is None:
            return
        if self.verticalScrollBar().isSliderDown() or self.horizontalScrollBar().isSliderDown():
            self.append_timer.start(16)
            return
        text, loaded, total, thread = self._pending
        self._pending = None
        if thread is not self.loader_thread:
            thread.consumed.set()
            return
        if not self._started:
            self.file_encoding = thread.encoding
            self.file_newline = thread.newline
            self.file_bom = thread.bom
            if self._highlighter:
                self._highlighter.setDocument(None)
                self._highlighter = None
            self.setUndoRedoEnabled(False)
            super().clear()
            self.update_dyna_mode(text)
            self.update_insets()
            self._started = True
        vertical, horizontal = self.verticalScrollBar(), self.horizontalScrollBar()
        v, h = vertical.value(), horizontal.value()
        cursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        vertical.setValue(v)
        horizontal.setValue(h)
        self.document().setModified(False)
        self.load_label.setText(f'Loading {min(100, int(loaded * 100 / max(1, total)))}% '
                                f'({loaded / 1048576:.1f} / {total / 1048576:.1f} MB) — scroll/search available; editing after loading.')
        thread.consumed.set()

    def on_load_failed(self, message):
        if self.sender() is not self.loader_thread:
            return
        logger.error(f'Failed to load {self.current_file}: {message}')
        self._load_failed = True
        self.current_file = None if self._started else self._previous_file

    def on_load_finished(self):
        if self.sender() is not self.loader_thread:
            return
        self.is_loading = False
        self.setReadOnly(False)
        self.setUndoRedoEnabled(True)
        self.load_label.hide()
        self.update_markdown_mode()
        if not self._load_failed:
            self.file_encoding = self.loader_thread.encoding
            self.file_newline = self.loader_thread.newline
            self.file_bom = self.loader_thread.bom
            if Path(self.current_file).suffix.lower() == '.json' and self.document().characterCount() <= 1_000_000:
                try:
                    self.setPlainText(format_json(self.toPlainText()))
                except ValueError as error:
                    logger.warning(f'Invalid JSON; original text retained: {error_message(error)}')
            self.document().setModified(False)
            self.dropFile.emit(self.current_file)

    def update_markdown_mode(self):
        self.update_dyna_mode()
        markdown = bool(self.current_file and Path(self.current_file).suffix.lower() == '.md')
        self.markdown_button.setVisible(markdown)
        if self._highlighter:
            self._highlighter.setDocument(None)
            self._highlighter = None
        if markdown and self.document().characterCount() <= 1_000_000:
            self._highlighter = MarkdownHighlighter(self.document())
        if self.current_file and Path(self.current_file).suffix.lower() == '.json' and self.document().characterCount() <= 1_000_000:
            self._highlighter = JsonHighlighter(self.document())
        self.update_insets()

    def stop_loading(self):
        self.append_timer.stop()
        self._pending = None
        thread, self.loader_thread = self.loader_thread, None
        if thread:
            thread.stop()
        self.is_loading = False
        self.setReadOnly(False)
        self.setUndoRedoEnabled(True)
        self.load_label.hide()
        self.update_insets()

    def shutdown(self):
        self.stop_loading()
        for thread in tuple(self._workers):
            thread.stop()
        return all(thread.wait(2000) for thread in tuple(self._workers))

    @property
    def modified(self):
        return self.document().isModified()

    @modified.setter
    def modified(self, value):
        self.document().setModified(value)

    def clear(self):
        self.stop_loading()
        self.file_encoding, self.file_newline = 'utf-8', None
        self.file_bom = ''
        self.current_file = None
        super().clear()
        self.update_markdown_mode()
        self.hide_search()
