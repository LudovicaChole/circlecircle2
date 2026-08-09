from PySide6.QtCore import QDir
from PySide6.QtWidgets import (
    QTreeView,
    QFileSystemModel
)
from PySide6.QtCore import Qt


class C2FileTree(QTreeView):

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

    def set_directory(self, path):
        self.root_path = path

        self.model.setRootPath(
            path
        )

        self.setRootIndex(
            self.model.index(path)
        )

        self.clearFocus()