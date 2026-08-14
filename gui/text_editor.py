import os
from pathlib import Path
from PySide6.QtWidgets import (QPlainTextEdit, QWidget, QHBoxLayout,
                               QLineEdit, QPushButton)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QTextCursor, QTextDocument, QShortcut, QKeySequence


class FileLoaderThread(QThread):
    """
    后台文件加载线程
    负责在后台按块读取文件，防止阻塞主 UI
    """
    chunk_ready = Signal(str)
    finished_loading = Signal()

    def __init__(self, filepath, start_line=5000, chunk_size=5000, encoding="utf-8"):
        super().__init__()
        self.filepath = filepath
        self.start_line = start_line
        self.chunk_size = chunk_size
        self.encoding = encoding
        self._is_running = True

    def run(self):
        try:
            with open(self.filepath, "r", encoding=self.encoding, errors="replace") as f:
                # 1. 跳过已经被主线程读取的前 start_line 行
                for _ in range(self.start_line):
                    if not f.readline():
                        break

                # 2. 分块读取后续内容
                lines = []
                for line in f:
                    if not self._is_running:
                        break

                    lines.append(line.rstrip("\r\n"))

                    if len(lines) >= self.chunk_size:
                        self.chunk_ready.emit("\n" + "\n".join(lines))
                        lines = []
                        self.msleep(10)  # 稍微让出 CPU，保证 UI 流畅

                # 3. 发送最后剩余的行
                if lines and self._is_running:
                    self.chunk_ready.emit("\n" + "\n".join(lines))

        except Exception as e:
            print(f"[FileLoaderThread] Error: {e}")
        finally:
            self.finished_loading.emit()

    def stop(self):
        self._is_running = False


class C2TextEditor(QPlainTextEdit):
    dropFile = Signal(str)
    newFile = Signal()
    saveFile = Signal()
    openFile = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.current_file = None
        self.loader_thread = None
        self.is_loading = False

        self.setup_search_panel()

    # ===============================
    # 搜索功能 (Search Panel)
    # ===============================
    def setup_search_panel(self):
        """初始化悬浮搜索面板"""
        self.search_panel = QWidget(self)
        self.search_panel.setObjectName("SearchPanel")
        # 简单设置一下搜索框的背景，防止和文本混在一起
        self.search_panel.setStyleSheet("""
            QWidget#SearchPanel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)

        layout = QHBoxLayout(self.search_panel)
        layout.setContentsMargins(4, 4, 4, 4)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find...")
        self.search_input.returnPressed.connect(self.find_next)  # 回车键直接查找下一个

        self.btn_prev = QPushButton("▲")
        self.btn_prev.setToolTip("Find Previous")
        self.btn_prev.setFixedWidth(30)
        self.btn_prev.clicked.connect(self.find_prev)

        self.btn_next = QPushButton("▼")
        self.btn_next.setToolTip("Find Next")
        self.btn_next.setFixedWidth(30)
        self.btn_next.clicked.connect(self.find_next)

        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedWidth(30)
        self.btn_close.clicked.connect(self.hide_search)

        layout.addWidget(self.search_input)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.btn_close)

        self.search_panel.hide()

        # Ctrl+F
        self.shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_find.activated.connect(self.show_search)

        # Esc
        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(self.hide_search)

        # Ctrl+N
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.activated.connect(self.newFile.emit)

        # Ctrl+S
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.saveFile.emit)

        # Ctrl+O
        self.shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_open.activated.connect(self.openFile.emit)

    def resizeEvent(self, event):
        """当编辑器大小改变时，保证搜索框一直悬浮在右上角"""
        super().resizeEvent(event)
        panel_width = 250
        panel_height = 40
        x = self.width() - panel_width - 25  # 留出滚动条的空间
        y = 10
        self.search_panel.setGeometry(x, y, panel_width, panel_height)

    def show_search(self):
        """显示搜索框"""
        # 如果选中了文本，直接将选中的文本作为搜索词
        selected_text = self.textCursor().selectedText()
        if selected_text:
            self.search_input.setText(selected_text)

        self.search_panel.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def hide_search(self):
        """隐藏搜索框，并将焦点还给编辑器"""
        self.search_panel.hide()
        self.setFocus()

    def find_next(self):
        """查找下一个"""
        text = self.search_input.text()
        if not text:
            return

        # find() 方法会自动高亮并移动光标
        found = self.find(text)

        # 如果到底了没找到，则回到文档开头重新往下找 (Wrap around)
        if not found:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Start)
            self.setTextCursor(cursor)
            self.find(text)

    def find_prev(self):
        """查找上一个"""
        text = self.search_input.text()
        if not text:
            return

        # 使用 FindBackward 标志向后查找
        found = self.find(text, QTextDocument.FindBackward)

        # 如果到顶了没找到，则跳到文档末尾重新往上找
        if not found:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.setTextCursor(cursor)
            self.find(text, QTextDocument.FindBackward)

    # ===============================
    # 拖拽事件 (Drag & Drop)
    # ===============================
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            event.ignore()
            return

        path = urls[0].toLocalFile()
        if Path(path).is_file():
            self.open_file(path)
            event.acceptProposedAction()
        else:
            event.ignore()

    # ===============================
    # 文件打开与后台加载
    # ===============================
    def open_file(self, path):
        self.stop_loading()
        self.current_file = path
        self.is_loading = True

        initial_lines = []
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for _ in range(5000):
                    line = f.readline()
                    if not line:
                        break
                    initial_lines.append(line.rstrip("\r\n"))
        except Exception as e:
            print(f"Failed to open file: {e}")
            return

        self.setPlainText("\n".join(initial_lines))
        self.document().setModified(False)

        self.loader_thread = FileLoaderThread(path, start_line=5000, chunk_size=5000)
        self.loader_thread.chunk_ready.connect(self.on_chunk_ready)
        self.loader_thread.finished_loading.connect(self.on_load_finished)
        self.loader_thread.start()

    def on_chunk_ready(self, chunk_text):
        scrollbar = self.verticalScrollBar()
        current_scroll = scrollbar.value()

        was_modified = self.document().isModified()

        cursor = self.textCursor()
        user_position = cursor.position()

        cursor.movePosition(QTextCursor.End)
        cursor.insertText(chunk_text)

        cursor.setPosition(user_position)
        self.setTextCursor(cursor)
        scrollbar.setValue(current_scroll)

        self.document().setModified(was_modified)

    def on_load_finished(self):
        self.is_loading = False
        self.dropFile.emit(f"File fully loaded: {self.current_file}")

    def stop_loading(self):
        if self.loader_thread and self.loader_thread.isRunning():
            self.loader_thread.stop()
            self.loader_thread.wait()
            self.loader_thread = None
            self.is_loading = False

    # ===============================
    # 覆盖原生的属性（兼容原版接口）
    # ===============================
    @property
    def modified(self):
        return self.document().isModified()

    @modified.setter
    def modified(self, value):
        self.document().setModified(value)

    def clear(self):
        self.stop_loading()
        self.current_file = None
        super().clear()
        self.hide_search()