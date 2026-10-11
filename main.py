import logging
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                               QSplitter, QDialogButtonBox, QDialog, QLabel,
                               QComboBox, QFileDialog, QMessageBox, QFormLayout, QCheckBox)
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from gui.menu_bar import C2MenuBar
from gui.clear_fea import configure as configure_clear_fea
from gui.file_tree_bar import C2FileTree
from gui.status_bar import C2StatusBar
from gui.console_bar import C2Console, ConsoleLogHandler
from gui.text_editor import C2TextEditor
from gui.file_types import SOURCE_SOLVERS, TEXT_FILTER, TARGET_VERSIONS, MEDIA_EXTENSIONS, TEXT_EXTENSIONS
from gui.media_preview import MediaPreview
from gui.markdown_preview import MarkdownPreview
from gui.license_dialog import LicenseDialog
from utilities.error_messages import error_message
from utilities.licensing import LicenseManager, atomic_write
from core.fea.fea_keywords_translator import fea_keywords_translator
from core.fea.conversion_support import development_warning
from utilities.logger import logger
from utilities.device_info import device_report
from utilities.profile_settings import ProfileSettings
from utilities.app_paths import application_directory, resource_directory


class C2App(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setApplicationName('CircleCircle2')
        self.setObjectName('CircleCircle2')
        geometry = self.primaryScreen().availableGeometry()
        self.available_width = geometry.width()
        self.available_height = geometry.height()


class SelectDialog(QDialog):
    def __init__(self, parent=None, ext=None):
        super().__init__(parent)
        self.setWindowTitle('Select Solver and Version')
        self.resize(350, 160)
        layout = QFormLayout(self)
        self.solver_combo = QComboBox()
        source = SOURCE_SOLVERS.get((ext or '').lower(), (None, None))[0]
        names = {'abaqus': 'ABAQUS', 'lsdyna': 'Ls-Dyna', 'pamcrash': 'PamCrash'}
        self.solver_combo.addItems(name for name in TARGET_VERSIONS if name != names.get(source))
        self.version_combo = QComboBox()
        layout.addRow('Solver:', self.solver_combo)
        layout.addRow('Version:', self.version_combo)
        self.mapping_checkbox = QCheckBox('Use material mapping (Material_Library folder)')
        self.mapping_checkbox.setChecked(True)
        layout.addRow(self.mapping_checkbox)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
        self.solver_combo.currentTextChanged.connect(self.update_versions)
        self.update_versions(self.solver_combo.currentText())

    def update_versions(self, solver_name):
        self.version_combo.clear()
        self.version_combo.addItems(TARGET_VERSIONS.get(solver_name, ()))

    def get_selection(self):
        return {'solver': self.solver_combo.currentText(), 'version': self.version_combo.currentText(),
                'material_mapping': self.mapping_checkbox.isChecked()}


class TranslationThread(QThread):
    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, translator, options, parent=None):
        super().__init__(parent)
        self.translator, self.options = translator, options

    def run(self):
        try:
            self.translator.translate(**self.options)
        except Exception as error:
            if not getattr(error, 'fea_logged', False):
                logger.error(f'Translation failed: {error_message(error)}')
            self.failed.emit(error_message(error))
        else:
            self.succeeded.emit(self.options['file_path'])


class DeviceThread(QThread):
    reportReady = Signal(str)

    def run(self):
        try:
            self.reportReady.emit(device_report())
        except Exception as error:
            logger.error(f'Could not read device information: {error_message(error)}')


class MainWindow(QMainWindow):
    def __init__(self, app, license_manager=None, profile_settings=None):
        super().__init__()
        self.fea_keywords_translator = fea_keywords_translator
        self.license_manager = license_manager or LicenseManager()
        self.profile_settings = profile_settings or ProfileSettings()
        self.auxiliary_windows = set()
        self.translation_thread = None
        self.device_thread = None
        self.nn_dialog = None
        self.setObjectName('CircleCircle2_MainWindow')
        self.setWindowTitle('CircleCircle2')
        screen = app.primaryScreen().availableGeometry()
        width, height = int(screen.width() * .8), int(screen.height() * .8)
        self.resize(width, height)
        self.move(screen.x() + (screen.width() - width) // 2,
                  screen.y() + (screen.height() - height) // 2)
        self.menu_bar = C2MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.status_bar = C2StatusBar(self)
        self.setStatusBar(self.status_bar)
        center = QWidget()
        self.setCentralWidget(center)
        layout = QVBoxLayout(center)
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        self.file_tree = C2FileTree(self)
        main_splitter.addWidget(self.file_tree)
        right_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(right_splitter)
        self.text_editor = C2TextEditor(self)
        self.text_editor.apply_preferences(self.profile_settings.preferences())
        self.text_editor.stateChanged.connect(self.refresh_file_states)
        self.text_editor.document().modificationChanged.connect(self.refresh_file_states)
        right_splitter.addWidget(self.text_editor)
        self.console = C2Console(self)
        right_splitter.addWidget(self.console)
        self.log_handler = ConsoleLogHandler(self.console)
        logger.logger.setLevel(logging.DEBUG)
        logger.logger.addHandler(self.log_handler)
        logger.configure_profile(self.profile_settings)
        directory = self.profile_settings.work_directory()
        if directory:
            self.file_tree.set_directory(directory)
            self.status_bar.set_message(f'Work directory: {directory}')
        self.file_tree.openFile.connect(self.open_current_file)
        from gui.hwx_mesh import start_mesh
        self.hwx_thread = None
        self.file_tree.meshFile.connect(lambda path: start_mesh(self, path))
        self.file_tree.translateFile.connect(self.translate_file)
        self.file_tree.deleteFile.connect(self.on_deleted)
        self.text_editor.openRequested.connect(self.open_current_file)
        self.text_editor.mediaRequested.connect(self.show_media)
        self.text_editor.markdownRequested.connect(self.show_markdown)
        self.text_editor.dropFile.connect(self.drop_file)
        self.text_editor.newFile.connect(self.new_file)
        self.text_editor.saveFile.connect(self.save_file)
        self.text_editor.openFile.connect(self.open_file)
        self.console.commandEntered.connect(self.handle_command)
        self.init_menu_event()
        main_splitter.setSizes([500, 1000])
        right_splitter.setSizes([600, 300])
        QTimer.singleShot(0, self.report_license_status)

    def init_menu_event(self):
        from gui.preferences import configure_material_library, configure_unit, configure_editor
        self.menu_bar.material_library_path_action.triggered.connect(lambda: configure_material_library(self))
        self.menu_bar.unit_action.triggered.connect(lambda: configure_unit(self))
        self.menu_bar.editor_settings_action.triggered.connect(lambda: configure_editor(self))
        from gui.towing_nn import configure_translation
        for action, callback in (
            (self.menu_bar.towing_length_action, lambda: configure_translation(self)),
            (self.menu_bar.contact_action, lambda: QMessageBox.information(
                self, 'Contact', 'Email: ludovica.chole@icloud.com')),
            (self.menu_bar.towing_hook_nn_action, lambda: self.train_towing_nn('hook')),
            (self.menu_bar.towing_nn_action, lambda: self.train_towing_nn('towing')),
            (self.menu_bar.clear_fea_action, lambda: configure_clear_fea(self)),
            (self.menu_bar.new_action, self.new_file),
            (self.menu_bar.open_action, self.open_file),
            (self.menu_bar.save_action, self.save_file),
            (self.menu_bar.save_as_action, self.save_as_file),
            (self.menu_bar.set_work_directory_action, self.set_work_directory),
            (self.menu_bar.close_action, self.close),
            (self.menu_bar.license_action, self.show_license),
            (self.menu_bar.device_action, self.show_device),
            (self.menu_bar.translate_action, self.translate_current_file),
            (self.menu_bar.documentation_action, self.show_documentation),
        ):
            action.triggered.connect(callback)

    def train_towing_nn(self, kind):
        if not self.report_license_status(announce=False).valid:
            QMessageBox.warning(self, 'Activation Required', 'Activate the software in Setting > License to use NN training and validation.')
            return
        if self.nn_dialog is not None:
            self.nn_dialog.raise_()
            self.nn_dialog.activateWindow()
            return
        from gui.towing_nn import TrainingDialog
        dialog = TrainingDialog(kind, self, license_manager=self.license_manager)
        self.nn_dialog = dialog
        dialog.finished.connect(lambda result: setattr(self, 'nn_dialog', None))
        dialog.setAttribute(Qt.WA_DeleteOnClose)
        dialog.show()

    def report_license_status(self, announce=True):
        status = self.license_manager.status()
        if status.valid and announce:
            logger.info(f'License valid until {status.expires_at}; IPv4: {status.ipv4}')
        elif not status.valid:
            logger.warning('License unavailable. Please activate the software. ' + status.message)
        return status

    def show_license(self):
        LicenseDialog(self.license_manager, self).exec()

    def keep_window(self, window):
        self.auxiliary_windows.add(window)
        def removed(*_):
            self.auxiliary_windows.discard(window)
            self.refresh_file_states()
        window.destroyed.connect(removed)
        window.show()
        self.refresh_file_states()
        return window

    def refresh_file_states(self, *_):
        states = {}
        def add(path, label):
            if path:
                key = self.file_tree.model.path_key(path)
                states.setdefault(key, set()).add(label)
        editor = self.text_editor
        if editor.current_file:
            add(editor.current_file, 'Loading' if editor.is_loading else 'Open')
            if editor.modified and not editor.is_loading:
                add(editor.current_file, 'Modified')
        for window in self.auxiliary_windows:
            add(getattr(window, 'path', None) or getattr(window, 'source_path', None), 'Preview')
        if self.translation_thread is not None:
            add(self.translation_thread.options['file_path'], 'Translating')
        self.file_tree.model.set_file_states(states)

    def show_media(self, path):
        try:
            return self.keep_window(MediaPreview(path, self))
        except (OSError, ValueError) as error:
            logger.error(error_message(error))

    def show_markdown(self):
        if self.text_editor.is_loading:
            logger.info('Please wait until loading finishes before rendering Markdown.')
            return
        path = self.text_editor.current_file
        return self.keep_window(MarkdownPreview(
            f'{Path(path).name if path else "Untitled"} — Markdown Preview',
            self.text_editor.toPlainText(), self, source_path=path))

    def show_documentation(self):
        path = resource_directory() / 'help_documentation' / 'documentation.md'
        try:
            return self.keep_window(MarkdownPreview('CircleCircle2 — Documentation',
                                                     path.read_text(encoding='utf-8'), self, source_path=path,
                                                     documentation=True))
        except OSError as error:
            logger.error(f'Cannot open documentation: {error_message(error)}')

    def show_device(self):
        if self.device_thread is not None:
            logger.info('Device information is already being collected.')
            return
        logger.info('Reading CPU, GPU, network addresses and current date…')
        self.console.begin_operation('DEVICE')
        self.device_thread = DeviceThread(self)
        self.device_thread.reportReady.connect(self.console.append_message)
        self.device_thread.finished.connect(self.device_finished)
        self.device_thread.start()

    def device_finished(self):
        thread, self.device_thread = self.device_thread, None
        thread.deleteLater()

    def confirm_unsaved(self):
        if not self.text_editor.modified:
            return True
        answer = QMessageBox.question(self, 'Save File', 'Current file has been modified. Save?',
                                      QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                                      QMessageBox.Save)
        if answer == QMessageBox.Save:
            return self.save_file()
        return answer == QMessageBox.Discard

    def drop_file(self, file_path):
        self.status_bar.set_message(f'Loaded: {file_path}')
        logger.info(f'Loaded: {file_path}')

    def new_file(self):
        if self.confirm_unsaved():
            self.text_editor.clear()
            self.text_editor.modified = False
            self.status_bar.set_message('New File')

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open File', self.file_tree.root_path, TEXT_FILTER)
        if path:
            self.open_current_file(path)

    def open_current_file(self, file_path):
        if file_path and Path(file_path).suffix.lower() not in (*TEXT_EXTENSIONS, *MEDIA_EXTENSIONS):
            message = f'Unsupported file type: {Path(file_path).name}. This file cannot be opened in the editor.'
            logger.warning(message)
            QMessageBox.warning(self, 'Unsupported File', message)
            return
        if file_path and Path(file_path).suffix.lower() in MEDIA_EXTENSIONS:
            self.show_media(file_path)
            return
        if file_path and self.confirm_unsaved():
            self.console.begin_operation(f'OPEN · {Path(file_path).name}')
            self.text_editor.open_file(file_path)

    def write_editor(self, path):
        if self.text_editor.is_loading:
            logger.warning('The file is still loading. Please wait before saving.')
            return False
        try:
            atomic_write(path, self.text_editor.file_bom + self.text_editor.toPlainText(),
                         encoding=self.text_editor.file_encoding,
                         newline=self.text_editor.file_newline)
        except (OSError, ValueError) as error:
            logger.error(f'Cannot save {path}: {error_message(error)}')
            QMessageBox.warning(self, 'Save Failed', error_message(error))
            return False
        self.text_editor.current_file = str(path)
        self.text_editor.modified = False
        self.text_editor.update_markdown_mode()
        self.status_bar.set_message(f'Saved: {path}')
        logger.info(f'Saved: {path}')
        return True

    def save_file(self):
        path = self.text_editor.current_file
        return self.write_editor(path) if path else self.save_as_file()

    def save_as_file(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save File',
                                             self.text_editor.current_file or self.file_tree.root_path,
                                             TEXT_FILTER)
        return self.write_editor(path) if path else False

    def set_work_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Work Directory', self.file_tree.root_path)
        if directory:
            try:
                self.profile_settings.save_work_directory(directory)
            except (OSError, ValueError) as error:
                logger.error(f'Cannot save work directory: {error_message(error)}')
                return
            logger.configure_profile(self.profile_settings)
            self.file_tree.set_directory(directory)
            self.status_bar.set_message(directory)
            logger.info(f'Work directory: {directory}')

    def on_deleted(self, deleted_path):
        current = self.text_editor.current_file
        if current and (Path(current) == Path(deleted_path) or Path(deleted_path) in Path(current).parents):
            self.text_editor.stop_loading()
            self.text_editor.current_file = None
            self.text_editor.modified = True
            self.status_bar.set_message('Source deleted. Editor text retained; use Save As to keep it.')

    def translate_current_file(self):
        rows = self.file_tree.selectionModel().selectedRows(0)
        if self.file_tree.hasFocus() and len(rows) > 1:
            logger.warning('Please select one solver file to translate.')
            return
        path = self.text_editor.current_file
        if self.file_tree.hasFocus() or not path:
            if len(rows) == 1 and not self.file_tree.model.isDir(rows[0]):
                path = self.file_tree.model.filePath(rows[0])
        if not path:
            logger.warning('Open or select a solver file before using Translate.')
            return
        self.translate_file(path)

    def translate_file(self, file_path):
        ext = Path(file_path).suffix.lower()
        if ext not in SOURCE_SOLVERS or not Path(file_path).is_file():
            logger.warning(f'This file does not support Translate: {file_path}')
            return
        if self.translation_thread is not None:
            logger.warning('A translation is already running. Please wait for it to finish.')
            return
        if not self.report_license_status(announce=False).valid:
            return
        current = self.text_editor.current_file
        if current and Path(current).resolve() == Path(file_path).resolve() and not self.confirm_unsaved():
            return
        dialog = SelectDialog(self, ext)
        if dialog.exec() != QDialog.Accepted:
            return
        if not self.report_license_status(announce=False).valid:
            return
        selection = dialog.get_selection()
        solver, version = SOURCE_SOLVERS[ext]
        self.console.begin_operation(f'TRANSLATE · {Path(file_path).name}')
        warning = development_warning(solver, selection['solver'], selection['version'])
        if warning:
            logger.warning(warning)
            self.status_bar.set_message(warning)
            return
        mapping = selection.get('material_mapping', False)
        mapping_path = None
        if mapping:
            from core.fea.material_catalog import default_catalog_path
            mapping_path = str(default_catalog_path())
        options = dict(file_path=str(file_path), solver1=solver, version1=version,
                       solver2=selection['solver'], version2=selection['version'], material_mapping=mapping,
                       material_mapping_file_path=mapping_path)
        if solver == 'lsdyna' and selection['solver'].lower() == 'abaqus':
            from utilities.towing_settings import load
            try:
                options['towing_options'] = load()
            except (OSError, ValueError) as error:
                logger.error(f'Cannot read towing settings: {error}')
                return
        self.translation_thread = TranslationThread(self.fea_keywords_translator, options, self)
        self.translation_thread.succeeded.connect(self.translation_succeeded)
        self.translation_thread.failed.connect(self.translation_failed)
        self.translation_thread.finished.connect(self.translation_finished)
        self.refresh_file_states()
        logger.info(f'Translating {file_path} → {selection["solver"]} {selection["version"]}')
        self.status_bar.set_message(f'Translating: {file_path}')
        self.translation_thread.start()

    def translation_succeeded(self, path):
        logger.info(f'Translation completed: {path}')
        self.status_bar.set_message(f'Translation completed: {path}')

    def translation_failed(self, message):
        self.status_bar.set_message('Translation failed — see Console for details.')

    def translation_finished(self):
        thread, self.translation_thread = self.translation_thread, None
        self.refresh_file_states()
        thread.deleteLater()

    def handle_command(self, command):
        commands = {'-open': self.open_file, '-save': self.save_file, '-save as': self.save_as_file,
                    '-set work directory': self.set_work_directory, '-new': self.new_file,
                    '-close': self.close, '-license': self.show_license, '-device': self.show_device,
                    '-translate': self.translate_current_file, '-documentation': self.show_documentation,
                    '-nn': lambda: self.train_towing_nn('hook')}
        command = command.strip().lower()
        if command == '-help':
            self.console.append_message('Available commands:\n' + '\n'.join(commands) + '\n-help')
        elif command in commands:
            try:
                commands[command]()
            except Exception as error:
                logger.error(f'Command failed: {error_message(error)}')
        else:
            logger.error(f'Unknown command: {command}')

    def closeEvent(self, event):
        if self.nn_dialog is not None and self.nn_dialog.worker is not None:
            QMessageBox.information(self, 'Training Running', 'Cancel or finish NN training before closing.')
            event.ignore()
            return
        if self.translation_thread is not None or self.device_thread is not None or self.hwx_thread is not None:
            QMessageBox.information(self, 'Task Running', 'Please wait for the current task to finish before closing.')
            event.ignore()
            return
        if not self.confirm_unsaved():
            event.ignore()
            return
        if not self.text_editor.shutdown():
            logger.warning('The file reader is still stopping. Please try closing again shortly.')
            event.ignore()
            return
        for window in tuple(self.auxiliary_windows):
            window.close()
        logger.logger.removeHandler(self.log_handler)
        self.log_handler.close()
        if not any(isinstance(handler, ConsoleLogHandler) for handler in logger.logger.handlers):
            logger.close_file()
        event.accept()


def main():
    app = C2App()
    main_window = MainWindow(app)
    main_window.show()
    if any(argument.lower() == '-nn' for argument in sys.argv[1:]):
        QTimer.singleShot(0, lambda: main_window.train_towing_nn('hook'))
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
