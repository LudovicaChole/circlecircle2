import re
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor, QTextBlockFormat
from PySide6.QtWidgets import (QMainWindow, QTextBrowser, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QSplitter,
                               QListWidget, QListWidgetItem)


class MarkdownHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        if len(text) > 20000:
            return
        code = QTextCharFormat()
        code.setForeground(QColor('#087f5b'))
        code.setBackground(QColor('#edf7f1'))
        if text.lstrip().startswith('```'):
            self.setCurrentBlockState(0 if self.previousBlockState() == 1 else 1)
            self.setFormat(0, len(text), code)
            return
        if self.previousBlockState() == 1:
            self.setCurrentBlockState(1)
            self.setFormat(0, len(text), code)
            return
        self.setCurrentBlockState(0)
        heading = re.match(r'^#{1,6}\s', text)
        if heading:
            style = QTextCharFormat()
            style.setForeground(QColor('#1d4ed8'))
            style.setFontWeight(QFont.Bold)
            self.setFormat(0, len(text), style)
        for pattern, color, bold in ((r'\*\*[^*]+\*\*', '#7c3aed', True),
                                      (r'`[^`]+`', '#087f5b', False),
                                      (r'\[[^\]]+\]\([^)]+\)', '#0369a1', False),
                                      (r'^\s*(?:[-*+] |\d+\. |>).*', '#475569', False)):
            style = QTextCharFormat()
            style.setForeground(QColor(color))
            style.setFontWeight(QFont.Bold if bold else QFont.Normal)
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), style)


class MarkdownPreview(QMainWindow):
    def __init__(self, title, text, parent=None, source_path=None, documentation=False):
        super().__init__(parent, Qt.Window)
        self.source_path = source_path
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(title)
        self.resize(850, 720)
        self.contents = None
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setStyleSheet('QTextBrowser { background: #fff; color: #1e293b; padding: 24px; font-size: 14px; }')
        if source_path:
            self.browser.document().setBaseUrl(QUrl.fromLocalFile(str(source_path)))
        self.setCentralWidget(self.browser)
        if documentation:
            self.resize(1100, 780)
            root = QWidget()
            root.setStyleSheet('''
                QWidget { background: #f8fafc; color: #334155; }
                QLabel#DocumentationTitle { font-size: 22px; font-weight: 600; color: #1e293b; }
                QLabel#DocumentationHint { color: #64748b; }
                QListWidget { background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px; }
                QListWidget::item { padding: 10px 6px; border-radius: 5px; }
                QListWidget::item:selected { background: #dbeafe; color: #1d4ed8; }
                QListWidget::item:hover { background: #eff6ff; }
                QTextBrowser { background: white; color: #1e293b; border: 1px solid #cbd5e1;
                               border-radius: 8px; padding: 24px; font-size: 15px; }
                QPushButton { min-height: 30px; padding: 3px 16px; }
            ''')
            layout = QVBoxLayout(root)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(16)
            header = QHBoxLayout()
            titles = QVBoxLayout()
            heading = QLabel('Documentation')
            heading.setObjectName('DocumentationTitle')
            titles.addWidget(heading)
            hint = QLabel('CircleCircle2 user guide · Select a section to jump to it')
            hint.setObjectName('DocumentationHint')
            titles.addWidget(hint)
            header.addLayout(titles, 1)
            close = QPushButton('Close')
            close.clicked.connect(self.close)
            header.addWidget(close)
            layout.addLayout(header)
            split = QSplitter(Qt.Horizontal)
            sidebar = QWidget()
            navigation = QVBoxLayout(sidebar)
            navigation.setContentsMargins(0, 0, 0, 0)
            navigation.addWidget(QLabel('CONTENTS'))
            self.contents = QListWidget()
            self.contents.setWordWrap(True)
            self.contents.itemClicked.connect(self.jump_to_section)
            navigation.addWidget(self.contents)
            split.addWidget(sidebar)
            self.browser.setStyleSheet('')
            split.addWidget(self.browser)
            split.setChildrenCollapsible(False)
            split.setStretchFactor(1, 1)
            split.setSizes([240, 800])
            layout.addWidget(split, 1)
            self.setCentralWidget(root)
        self.set_markdown(text)

    def set_markdown(self, text):
        limit = 1_000_000
        if len(text) > limit:
            text = '> Preview shows the first 1,000,000 characters. The editor retains the complete file.\n\n' + text[:limit]
        self.browser.setMarkdown(text)
        if self.contents is not None:
            self.contents.clear()
            block = self.browser.document().begin()
            while block.isValid():
                block_format = block.blockFormat()
                level = block_format.headingLevel()
                block_format.setTopMargin(16 if level else 0)
                block_format.setBottomMargin(10)
                block_format.setLineHeight(135, QTextBlockFormat.ProportionalHeight.value)
                cursor = QTextCursor(block)
                cursor.setBlockFormat(block_format)
                if level in (1, 2, 3):
                    item = QListWidgetItem(block.text())
                    item.setData(Qt.UserRole, block.position())
                    self.contents.addItem(item)
                block = block.next()

    def jump_to_section(self, item):
        cursor = QTextCursor(self.browser.document())
        cursor.setPosition(item.data(Qt.UserRole))
        self.browser.setTextCursor(cursor)
        self.browser.ensureCursorVisible()
