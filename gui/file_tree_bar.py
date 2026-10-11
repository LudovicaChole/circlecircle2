import os
import shutil
from pathlib import Path
from PySide6.QtCore import QDir, Qt, Signal, QMimeData, QUrl
from PySide6.QtGui import QKeySequence, QColor, QFont, QBrush
from PySide6.QtWidgets import QApplication
from gui.clear_fea import cleanup_candidates, keep_extensions, keep_names, is_link
from collections import Counter
from PySide6.QtWidgets import (QTreeView, QFileSystemModel, QMenu, QMessageBox,
                               QDialog, QFormLayout, QLineEdit, QComboBox,
                               QDialogButtonBox, QInputDialog, QHeaderView)
from gui.file_types import SOURCE_SOLVERS, TEXT_EXTENSIONS
from utilities.error_messages import error_message
from utilities.logger import logger


class FileTreeModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_states = {}

    @staticmethod
    def path_key(path):
        return os.path.normcase(os.path.abspath(path))

    def set_file_states(self, states):
        updated = {self.path_key(path): tuple(sorted(labels)) for path, labels in states.items()}
        previous, self.file_states = self.file_states, updated
        for path in previous.keys() | updated.keys():
            if previous.get(path) == updated.get(path):
                continue
            index = self.index(path)
            if index.isValid():
                self.dataChanged.emit(index, index.siblingAtColumn(3),
                                      [Qt.DisplayRole, Qt.BackgroundRole, Qt.ForegroundRole,
                                       Qt.FontRole, Qt.ToolTipRole])

    def data(self, index, role=Qt.DisplayRole):
        labels = self.file_states.get(self.path_key(self.filePath(index))) if index.isValid() else None
        if labels:
            if role == Qt.DisplayRole and index.column() == 0:
                return super().data(index, role) + '  [' + ' · '.join(labels) + ']'
            if role == Qt.ToolTipRole:
                return self.filePath(index) + '\nCircleCircle2: ' + ', '.join(labels)
            if role == Qt.BackgroundRole:
                color = '#fef3c7' if 'Modified' in labels else '#ede9fe' if any(
                    label in labels for label in ('Loading', 'Translating')) else '#dbeafe'
                return QBrush(QColor(color))
            if role == Qt.ForegroundRole:
                return QBrush(QColor('#172554'))
            if role == Qt.FontRole:
                font = QFont()
                font.setBold(True)
                return font
        return super().data(index, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return {0: 'Name', 1: 'Size', 3: 'Date'}.get(section, 'Type')
        return super().headerData(section, orientation, role)


def checked_child(directory, name):
    """Creation names must be single, portable filenames, never paths."""
    name = name.strip()
    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)),
                *(f'LPT{i}' for i in range(1, 10))}
    if (not name or name in ('.', '..') or name.endswith(('.', ' '))
            or any(c in name for c in '<>:"/\\|?*') or any(ord(c) < 32 for c in name)
            or name.split('.')[0].upper() in reserved):
        raise ValueError('Please enter a valid name without a path or reserved characters.')
    parent = Path(directory).resolve(strict=True)
    if not parent.is_dir():
        raise ValueError('The destination folder no longer exists.')
    return parent / name


class NewFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New File')
        layout = QFormLayout(self)
        self.name_edit = QLineEdit('untitled')
        self.extension_combo = QComboBox()
        self.extension_combo.addItems(TEXT_EXTENSIONS)
        layout.addRow('Name:', self.name_edit)
        layout.addRow('File type:', self.extension_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def filename(self):
        name = self.name_edit.text().strip()
        if not name:
            raise ValueError('A filename is required.')
        suffix = Path(name).suffix.lower()
        if suffix:
            if suffix not in TEXT_EXTENSIONS:
                raise ValueError('Unsupported file extension. Choose a file type from the list.')
            name = name[:-len(suffix)]
        return name + self.extension_combo.currentText()


class C2FileTree(QTreeView):
    openFile = Signal(str)
    meshFile = Signal(str)
    openInHM = Signal()
    translateFile = Signal(str)
    deleteFile = Signal(str)  # Emitted only after deletion succeeds.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FileTreeModel(self)
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.setModel(self.model)
        self.set_directory(QDir.currentPath())
        self.setColumnHidden(2, True)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setEditTriggers(QTreeView.NoEditTriggers)
        self.setSelectionMode(QTreeView.ExtendedSelection)
        self.setSelectionBehavior(QTreeView.SelectRows)
        self.setDragEnabled(True)
        self.setDragDropMode(QTreeView.DragOnly)
        self.setAcceptDrops(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.doubleClicked.connect(self.open_index)

    def set_directory(self, path):
        self.root_path = str(Path(path).resolve())
        self.model.setRootPath(self.root_path)
        self.setRootIndex(self.model.index(self.root_path))

    def open_index(self, index):
        if index.isValid() and not self.model.isDir(index):
            self.openFile.emit(self.model.filePath(index))

    def context_menu(self, index):
        menu = QMenu(self)
        path = self.model.filePath(index) if index.isValid() else self.root_path
        is_dir = not index.isValid() or self.model.isDir(index)
        if is_dir:
            menu.addAction('New Folder…', lambda: self.create_folder(path))
            menu.addAction('New File…', lambda: self.create_file(path))
        else:
            menu.addAction('Open', lambda: self.openFile.emit(path))
        menu.addAction('Open in File Explorer', lambda: self.open_in_explorer(path))
        if index.isValid():
            menu.addAction('Copy', self.copy_selected)
        menu.addAction('Copy Path', lambda: QApplication.clipboard().setText(os.path.normpath(os.path.abspath(path))))
        menu.addAction('Paste', self.paste_copied)
        if index.isValid():
            menu.addAction('Delete', self.delete_selected)
            if is_dir:
                menu.addSeparator()
                menu.addAction('Clear FEA Result', lambda: self.clear_fea(path))
            elif Path(path).suffix.lower() == '.hm':
                menu.addSeparator()
                menu.addAction('hwx_mesh', lambda: self.meshFile.emit(path))
            elif Path(path).suffix.lower() in SOURCE_SOLVERS:
                menu.addSeparator()
                menu.addAction('Translate', lambda: self.translateFile.emit(path))
        return menu

    def open_in_explorer(self, path):
        import subprocess
        from PySide6.QtGui import QDesktopServices
        path = os.path.normpath(os.path.abspath(path))
        try:
            if os.name == 'nt' and Path(path).is_file():
                subprocess.Popen(['explorer.exe', '/select,', path])
            elif not QDesktopServices.openUrl(QUrl.fromLocalFile(path)):
                raise OSError('File Explorer could not open the selected path.')
        except OSError as error:
            self.report_error(error)

    def show_context_menu(self, position):
        index = self.indexAt(position)
        if index.isValid() and not self.selectionModel().isRowSelected(index.row(), index.parent()):
            self.setCurrentIndex(index)
        menu = self.context_menu(index)
        menu.exec(self.viewport().mapToGlobal(position))
        menu.deleteLater()

    def report_error(self, error):
        logger.error(error_message(error))
        QMessageBox.warning(self, 'File Operation Failed', error_message(error))

    def create_file(self, directory):
        dialog = NewFileDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        try:
            path = checked_child(directory, dialog.filename())
            with path.open('x', encoding='utf-8'):
                pass
        except (OSError, ValueError) as error:
            self.report_error(error)
            return
        logger.info(f'Created file: {path}')
        self.openFile.emit(str(path))

    def create_folder(self, directory):
        name, accepted = QInputDialog.getText(self, 'New Folder', 'Folder name:')
        if not accepted:
            return
        try:
            path = checked_child(directory, name)
            path.mkdir()
        except (OSError, ValueError) as error:
            self.report_error(error)
            return
        logger.info(f'Created folder: {path}')

    def selected_paths(self):
        paths = [Path(self.model.filePath(i)) for i in self.selectionModel().selectedRows(0)]
        return self.top_level_paths(paths)

    @staticmethod
    def top_level_paths(paths):
        paths = list(dict.fromkeys(Path(os.path.abspath(p)) for p in paths))
        return [p for p in paths if not any(other in p.parents for other in paths if other != p)]

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
        elif event.key() == Qt.Key_Space:
            index = self.currentIndex()
            from gui.file_types import MEDIA_EXTENSIONS
            if index.isValid() and Path(self.model.filePath(index)).suffix.lower() in MEDIA_EXTENSIONS:
                self.open_index(index)
        elif event.matches(QKeySequence.Copy):
            self.copy_selected()
        elif event.matches(QKeySequence.Paste):
            self.paste_copied()
        else:
            return super().keyPressEvent(event)
        event.accept()

    def copy_selected(self):
        paths = self.selected_paths()
        if paths:
            mime = QMimeData()
            mime.setUrls([QUrl.fromLocalFile(str(p)) for p in paths])
            QApplication.clipboard().setMimeData(mime)

    def paste_copied(self):
        mime = QApplication.clipboard().mimeData()
        paths = self.top_level_paths([u.toLocalFile() for u in mime.urls() if u.isLocalFile()])
        index = self.currentIndex()
        current = Path(self.model.filePath(index)) if index.isValid() else Path(self.root_path)
        # Copying a selected folder in place creates its sibling, not a recursive copy.
        destination = current if current.is_dir() and current not in paths else current.parent
        if not index.isValid():
            destination = Path(self.root_path)
        for source in paths:
            try:
                if is_link(source):
                    raise ValueError('Copying linked files or folders is not supported.')
                if source.is_dir() and (destination.resolve() == source.resolve() or source.resolve() in destination.resolve().parents):
                    raise ValueError('Cannot copy a folder into itself.')
                stem, suffix = (source.name, '') if source.is_dir() else (source.stem, source.suffix)
                number = 1
                while True:
                    target = destination / f'{stem}_copy{number if number > 1 else ""}{suffix}'
                    if not os.path.lexists(target):
                        break
                    number += 1
                if source.is_dir():
                    # Reject nested links before copying so no external trees are followed.
                    for folder, dirs, files in os.walk(source, followlinks=False):
                        if any(is_link(Path(folder) / n) for n in dirs + files):
                            raise ValueError('Folder contains linked items and cannot be copied.')
                    shutil.copytree(source, target)
                else:
                    with source.open('rb') as src, target.open('xb') as dst:
                        shutil.copyfileobj(src, dst)
                    shutil.copystat(source, target)
                logger.info(f'Copied: {source} → {target}')
            except (OSError, ValueError) as error:
                self.report_error(error)

    def checked_target(self, path):
        target = Path(os.path.abspath(path))
        root = Path(self.root_path).resolve()
        target.parent.resolve().relative_to(root)
        if target == root or not os.path.lexists(target):
            raise ValueError('This item cannot be deleted from the current file tree.')
        if not is_link(target):
            target.resolve().relative_to(root)
        return target

    def delete_path(self, path):
        self.delete_paths([Path(path)])

    def delete_selected(self):
        self.delete_paths(self.selected_paths())

    def delete_paths(self, paths):
        try:
            targets = [self.checked_target(p) for p in self.top_level_paths(paths)]
        except (OSError, ValueError) as error:
            self.report_error(error)
            return
        if not targets:
            return
        answer = QMessageBox.question(self, 'Confirm Delete',
            f'Permanently delete {len(targets)} selected items and all folder contents?\n\n' +
            '\n'.join(str(p) for p in targets), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes:
            return
        for target in targets:
            try:
                self.checked_target(target)
                if target.is_symlink():
                    target.unlink()
                elif is_link(target):
                    target.rmdir()
                elif target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                logger.info(f'Deleted: {target}')
                self.deleteFile.emit(str(target))
            except (OSError, ValueError) as error:
                self.report_error(error)

    def clear_fea(self, directory):
        try:
            root = Path(directory).resolve(strict=True)
            root.relative_to(Path(self.root_path).resolve())
            keep = keep_extensions()
            names = keep_names()
            candidates = cleanup_candidates(directory, keep, names)
            if not candidates:
                QMessageBox.information(self, 'Clear FEA Result', 'No files need to be removed.')
                return
            counts = Counter(p.suffix.lower() or '(no extension)' for p in candidates)
            detail = '\n'.join(f'{ext}: {count}' for ext, count in sorted(counts.items()))
            answer = QMessageBox.question(self, 'Clear FEA Result',
                f'Permanently delete {len(candidates)} files in {root} (including subfolders)?\n\n'
                + detail + '\n\nPreserved extensions: ' + ', '.join(keep)
                + '\nPreserved exact filenames: ' + ', '.join(names),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if answer != QMessageBox.Yes:
                return
            for path in candidates:
                self.checked_target(path)
                if is_link(path) or any(is_link(p) for p in path.parents if p != root and root in p.parents):
                    raise ValueError('A linked folder was detected; cleanup stopped.')
                path.unlink()
                self.deleteFile.emit(str(path))
            logger.info(f'Cleared {len(candidates)} FEA result files from {root}')
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.report_error(error)
