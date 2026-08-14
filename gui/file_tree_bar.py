from PySide6.QtCore import QDir, Qt, Signal
from PySide6.QtWidgets import QTreeView, QFileSystemModel, QMenu
from PySide6.QtGui import QAction


class C2FileTree(QTreeView):
    openFile = Signal(str)
    openInHM = Signal()
    translateFile = Signal(str)
    deleteFile = Signal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setFocusPolicy(
            Qt.NoFocus
        )

        self.model = QFileSystemModel()

        self.root_path = QDir.currentPath()

        self.model.setRootPath(
            self.root_path
        )

        self.setModel(
            self.model
        )

        self.setRootIndex(
            self.model.index(
                self.root_path
            )
        )

        # drag
        self.setDragEnabled(True)

        self.setDragDropMode(
            QTreeView.DragOnly
        )

        self.setAcceptDrops(False)

        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_directory(self, path):
        self.root_path = path

        self.model.setRootPath(
            path
        )

        self.setRootIndex(
            self.model.index(path)
        )

        self.clearFocus()

    def show_context_menu(self, position):
        index = self.indexAt(position)

        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        is_dir = self.model.isDir(index)

        menu = QMenu(self)

        action_open = QAction("Open", self)
        action_open_in_hm = QAction("Open in HM", self)
        action_translate = QAction("Translate", self)
        action_delete = QAction("Delete", self)

        menu.addAction(action_open)
        menu.addAction(action_open_in_hm)
        menu.addAction(action_translate)
        menu.addSeparator()
        menu.addAction(action_delete)

        global_pos = self.viewport().mapToGlobal(position)

        selected_action = menu.exec(global_pos)

        if selected_action == action_open:
            self.openFile.emit(file_path)

        elif selected_action == action_open_in_hm:
            self.openInHM.emit()

        elif selected_action == action_translate:
            self.translateFile.emit(file_path)

        elif selected_action == action_delete:
            self.deleteFile.emit()

        else:
            pass
