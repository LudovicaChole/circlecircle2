"""Independent non-modal image windows, including animated GIF playback."""
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImageReader, QPixmap, QMovie
from PySide6.QtWidgets import QMainWindow, QLabel, QScrollArea, QToolBar
from utilities.logger import logger


class MediaPreview(QMainWindow):
    def __init__(self, path, parent=None):
        super().__init__(parent, Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.path = Path(path)
        self.setWindowTitle(f'{self.path.name} — Image Preview')
        self.resize(800, 600)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.scroll = QScrollArea()
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(self.label)
        self.setCentralWidget(self.scroll)
        toolbar = QToolBar('Image')
        toolbar.setParent(self)
        toolbar.hide()
        self.fit_action = toolbar.addAction('Fit to Window')
        self.fit_action.setCheckable(True)
        self.fit_action.setChecked(True)
        self.fit_action.toggled.connect(self.update_image)
        toolbar.addAction('Actual Size', lambda: self.fit_action.setChecked(False))
        self.movie = None
        self.pixmap = QPixmap()
        if self.path.suffix.lower() == '.gif':
            self.movie = QMovie(str(self.path))
            self.movie.setParent(self)
            if not self.movie.isValid():
                raise ValueError(f'Cannot decode image: {self.path}')
            self.movie.jumpToFrame(0)
            self.original_size = self.movie.currentPixmap().size()
            self.label.setMovie(self.movie)
            self.movie.frameChanged.connect(self.resize_label)
            self.movie.error.connect(lambda *_: logger.error(f'GIF playback failed: {self.path}'))
            self.movie.start()
        else:
            reader = QImageReader(str(self.path))
            reader.setAutoTransform(True)
            image = reader.read()
            if image.isNull():
                raise ValueError(f'Cannot decode {self.path}: {reader.errorString()}')
            self.pixmap = QPixmap.fromImage(image)
            self.original_size = self.pixmap.size()
        self.statusBar().showMessage(f'{self.path}  |  {self.original_size.width()} × {self.original_size.height()}')
        self.update_image()

    def resize_label(self, *_):
        if self.movie:
            self.label.resize(self.movie.currentPixmap().size())

    def update_image(self, *_):
        if not hasattr(self, 'original_size'):
            return
        size = self.original_size
        if self.fit_action.isChecked():
            available = self.scroll.viewport().size() - QSize(8, 8)
            if available.width() > 0 and available.height() > 0:
                size = size.scaled(available, Qt.KeepAspectRatio)
        if self.movie:
            self.movie.setScaledSize(size)
        else:
            self.label.setPixmap(self.pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.label.resize(size)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()

    def closeEvent(self, event):
        if self.movie:
            self.movie.stop()
            self.label.clear()
            self.movie.setFileName('')  # Release the Windows file handle immediately.
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Space, Qt.Key_Escape):
            self.close()
        else:
            super().keyPressEvent(event)
