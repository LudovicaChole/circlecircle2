"""Shared, display-only solver highlighting, field ruler and line numbers."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (QSyntaxHighlighter, QTextBlockUserData, QTextCharFormat,
                           QColor, QPainter, QPen, QFont, QFontMetricsF)
from PySide6.QtWidgets import QWidget
from gui.lsdyna_format import State, Row, scan_line
from gui import abaqus_format, pamcrash_format
from pathlib import Path


SCANNERS = {'lsdyna': (State, scan_line), 'abaqus': (abaqus_format.State, abaqus_format.scan_line),
            'pamcrash': (pamcrash_format.State, pamcrash_format.scan_line)}
LABELS = {'lsdyna': 'LS-DYNA', 'abaqus': 'Abaqus', 'pamcrash': 'PAM-CRASH'}


def solver_for_file(path, sample=''):
    suffix = Path(path).suffix.lower() if path else ''
    if suffix == '.inc':
        # Both solvers use .inc. Prefer a keyword signature to the historical
        # PAM-CRASH extension default; inspect only a bounded opening sample.
        for line in sample.splitlines():
            stripped = line.lstrip()
            if not stripped or stripped.startswith(('$', '**')):
                continue
            if stripped.startswith('*'):
                return 'abaqus'
            if '/' in line[:8] or stripped.split()[0].upper() in pamcrash_format.FREE_TOP:
                return 'pamcrash'
        return 'pamcrash'
    return {'.k': 'lsdyna', '.key': 'lsdyna', '.inp': 'abaqus', '.geo': 'abaqus', '.pc': 'pamcrash'}.get(suffix, '')


class CardData(QTextBlockUserData):
    def __init__(self, row, after):
        super().__init__()
        self.row, self.after = row, after


class SolverHighlighter(QSyntaxHighlighter):
    def __init__(self, document, solver='lsdyna'):
        super().__init__(document)
        self.solver = solver
        self.state_type, self.scan = SCANNERS[solver]
        self.state_ids = {}
        self.styles = {}
        for name, color, background in (
                ('keyword', '#1d4ed8', '#eff6ff'), ('comment', '#718096', None),
                ('title', '#8b5e13', None), ('even', '#172554', '#edf4fc'),
                ('odd', '#172554', '#f8fafc')):
            style = QTextCharFormat()
            style.setForeground(QColor(color))
            if background:
                style.setBackground(QColor(background))
            # Bold can change fixed-pitch metrics on some platforms, so keep the
            # same font weight for every character of fixed-width data rows.
            self.styles[name] = style

    def highlightBlock(self, text):
        previous = self.currentBlock().previous().userData()
        before = previous.after if isinstance(previous, CardData) and isinstance(previous.after, self.state_type) else self.state_type()
        row, after = self.scan(text, before)
        self.setCurrentBlockUserData(CardData(row, after))
        state_id = self.state_ids.setdefault(after, len(self.state_ids))
        self.setCurrentBlockState(state_id)
        if row.kind in ('keyword', 'comment', 'title'):
            self.setFormat(0, len(text), self.styles[row.kind])
        elif row.kind in ('data', 'free'):
            for index, (start, end) in enumerate(row.spans):
                self.setFormat(start, max(0, min(end, len(text)) - start), self.styles['even' if index % 2 == 0 else 'odd'])
            if self.solver == 'pamcrash' and '/' in text[:8]:
                self.setFormat(0, min(8, len(text)), self.styles['keyword'])


def row_for(block):
    data = block.userData()
    return data.row if isinstance(data, CardData) else Row(note='Reading card layout...')


class SolverRuler(QWidget):
    HEIGHT = 80

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setToolTip('Solver field guides. Display only: no separators are saved.')

    def paintEvent(self, event):
        editor = self.editor
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#f0f5fb'))
        cursor = editor.textCursor()
        row = row_for(cursor.block())
        column = cursor.positionInBlock()
        cell_width = QFontMetricsF(editor.font()).horizontalAdvance('0')
        origin = editor.contentOffset().x() + editor.document().documentMargin()
        variable = row.kind == 'free' or (row.kind == 'keyword' and bool(row.spans))
        selected = next((i for i, (a, b) in enumerate(row.spans)
                         if a <= column < b or (variable and column == b)), None)
        status = f'{LABELS.get(editor.solver_mode, "Solver")} | {row.keyword or "No keyword"} | {row.mode} | Ln {cursor.blockNumber() + 1}, Col {column + 1}'
        if selected is not None:
            a, b = row.spans[selected]
            status += f' | {row.names[selected]}: ' + (f'columns {a + 1}-{b}' if b > a else 'empty field')
        if row.note:
            status += ' | ' + row.note
        painter.setPen(QColor('#1e3a5f'))
        info_font = QFont(editor.font())
        info_font.setPointSizeF(max(8, info_font.pointSizeF() - 1))
        painter.setFont(info_font)
        painter.drawText(QRectF(8, 1, self.width() - 16, 23), Qt.AlignVCenter,
                         painter.fontMetrics().elidedText(status, Qt.ElideRight, max(0, self.width() - 16)))
        self.setToolTip(status + ('\n' + row.note if row.note else ''))
        painter.setFont(editor.font())
        if not row.spans:
            painter.setPen(QColor('#64748b'))
            painter.drawText(QRectF(8, 27, self.width() - 16, 38), Qt.AlignVCenter,
                             row.note or 'Select a data card to see its field names and column ranges.')
            return
        # Free fields can be one character or empty: readable tiles avoid
        # implying that they must align to fixed text columns.
        tile_width = 125
        first = max(0, (selected or 0) - max(1, self.width() // tile_width) + 1) if variable else 0
        for index, (start, end) in enumerate(row.spans):
            left, width = origin + start * cell_width, (end - start) * cell_width
            if variable:
                left, width = 8 + (index - first) * tile_width, tile_width - 4
            if left + width < 0 or left > self.width() or width <= 0:
                continue
            rect = QRectF(left, 27, width, 24)
            painter.fillRect(rect, QColor('#bfdbfe' if index == selected else '#e2eaf5' if index % 2 == 0 else '#f8fafc'))
            painter.setPen(QColor('#365375'))
            painter.drawRect(rect)
            label = painter.fontMetrics().elidedText(row.names[index], Qt.ElideRight, max(0, int(width - 6)))
            painter.drawText(rect.adjusted(3, 0, -3, 0), Qt.AlignCenter, label)
            painter.setPen(QColor('#536981'))
            caption = f'{start + 1}-{end}' if end > start else 'empty'
            if variable:
                caption = f'#{index + 1} | ' + caption
            painter.drawText(QRectF(left + 2, 53, max(0, width - 4), 22), Qt.AlignCenter, caption)
        painter.setPen(QColor('#cbd5e1'))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)


class SolverGutter(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#f0f5fb'))
        painter.setFont(self.editor.font())
        active = self.editor.textCursor().blockNumber()
        for block, rect in visible_blocks(self.editor):
            painter.setPen(QColor('#1d4ed8' if block.blockNumber() == active else '#718096'))
            painter.drawText(QRectF(0, rect.y(), self.width() - 7, rect.height()),
                             Qt.AlignRight | Qt.AlignVCenter, str(block.blockNumber() + 1))


def visible_blocks(editor):
    block = editor.firstVisibleBlock()
    while block.isValid():
        rect = editor.blockBoundingGeometry(block).translated(editor.contentOffset())
        if rect.top() > editor.viewport().height():
            break
        if block.isVisible() and rect.bottom() >= 0:
            yield block, rect
        block = block.next()


def paint_field_guides(editor):
    painter = QPainter(editor.viewport())
    pen = QPen(QColor('#7e9ab8'))
    pen.setStyle(Qt.DotLine)
    painter.setPen(pen)
    cell_width = QFontMetricsF(editor.font()).horizontalAdvance('0')
    origin = editor.contentOffset().x() + editor.document().documentMargin()
    for block, rect in visible_blocks(editor):
        row = row_for(block)
        if row.kind != 'data':
            continue
        for _, end in row.spans:
            x = origin + end * cell_width
            if 0 <= x <= editor.viewport().width():
                painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
