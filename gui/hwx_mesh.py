"""Asynchronous file-tree entry point for local HyperMesh jobs."""
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMessageBox
from core.hmdesktop.mesh_launcher import mesh_file
from core.fea.material_catalog import default_catalog_path
from utilities.logger import logger


class MeshWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, source, catalog, parent):
        super().__init__(parent)
        self.source, self.catalog = source, catalog

    def run(self):
        try:
            self.completed.emit(mesh_file(self.source, self.catalog))
        except Exception as error:
            self.failed.emit(str(error))


def start_mesh(window, source):
    if getattr(window, 'hwx_thread', None) is not None:
        QMessageBox.warning(window, 'HyperMesh Running', 'Please wait for the current HyperMesh job to finish.')
        return
    try:
        catalog = default_catalog_path()
    except ValueError as error:
        QMessageBox.warning(window, 'hwx_mesh', str(error))
        return
    window.console.begin_operation('HWX MESH · '+source)
    worker = MeshWorker(source, catalog, window)
    window.hwx_thread = worker
    def complete(result):
        logger.info(f'hwx_mesh completed: {result["output"]}')
        QMessageBox.information(window, 'hwx_mesh', 'Mesh saved:\n'+result['output'])
    def failed(message):
        logger.error('hwx_mesh: '+message)
        QMessageBox.warning(window, 'hwx_mesh Failed', message)
    def finished():
        window.hwx_thread = None
        worker.deleteLater()
    worker.completed.connect(complete)
    worker.failed.connect(failed)
    worker.finished.connect(finished)
    worker.start()
