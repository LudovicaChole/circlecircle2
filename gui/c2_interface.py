import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QDialogButtonBox, QPushButton, QDialog, QLabel, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox
from gui.menu_bar import C2MenuBar
from gui.file_tree_bar import C2FileTree
from gui.status_bar import C2StatusBar
from gui.console_bar import C2Console
from gui.text_editor import C2TextEditor
from services.fea_keywords_translator import fea_keywords_translator


class C2App(QApplication):
    def __init__(self):
        super().__init__()

        self.setObjectName("CircleCircle2")

        primary_screen = self.primaryScreen()

        available_geometry = primary_screen.availableGeometry()

        self.available_width = available_geometry.width()

        self.available_height = available_geometry.height()


class SelectDialog(QDialog):
    def __init__(self, parent=None, ext=None):
        super().__init__(parent)
        self.setWindowTitle("Select Solver and Version")
        self.resize(300, 150)

        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        solver_label = QLabel("Solver:")
        self.solver_combo = QComboBox()

        if ext in [".key", ".k"]:
            self.solver_combo.addItems(["PamCrash", "ABAQUS", "Optistruct"])
        elif ext in [".inp", ".geo"]:
            self.solver_combo.addItems(["Ls-Dyna", "PamCrash", "Optistruct"])
        elif ext in [".pc", ".inc"]:
            self.solver_combo.addItems(["Ls-Dyna", "ABAQUS", "Optistruct"])
        else:
            self.solver_combo.addItems(["UserDefine"])

        name_layout.addWidget(solver_label)
        name_layout.addWidget(self.solver_combo)
        layout.addLayout(name_layout)

        version_layout = QHBoxLayout()
        version_label = QLabel("Version:")
        self.version_combo = QComboBox()

        version_layout.addWidget(version_label)
        version_layout.addWidget(self.version_combo)
        layout.addLayout(version_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.solver_combo.currentTextChanged.connect(self.update_versions)

        self.update_versions(self.solver_combo.currentText())

    def update_versions(self, solver_name):
        self.version_combo.clear()

        if solver_name == "PamCrash":
            self.version_combo.addItems(["2020", "2023"])
        elif solver_name == "ABAQUS":
            self.version_combo.addItems(["6.14", "2025", "2026"])
        elif solver_name == "Optistruct":
            self.version_combo.addItems(["2024", "2025", "2026"])
        elif solver_name == "Ls-Dyna":
            self.version_combo.addItems(["12.0", "13.0", "14.0"])
        else:
            self.version_combo.addItems(["0.0"])

    def get_selection(self):
        return {
            "solver": self.solver_combo.currentText(),
            "version": self.version_combo.currentText()
        }


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.fea_keywords_translator = fea_keywords_translator

        self.setObjectName("CircleCircle2_MainWindow")

        self.setWindowTitle("CircleCircle2")

        width = int(app.available_width * 0.8)

        height = int(app.available_height * 0.8)

        self.resize(
            width,
            height
        )

        # move center
        center_x = (app.available_width - width) // 2

        center_y = (app.available_height - height) // 2

        self.move(center_x, center_y)

        # menu bar
        self.menu_bar = C2MenuBar(self)

        self.setMenuBar(self.menu_bar)

        self.init_menu_event()

        # state bar
        self.status_bar = C2StatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.set_message("CircleCircle2 -> Version: 1.0")

        center_widget = QWidget()
        self.setCentralWidget(center_widget)

        layout = QVBoxLayout(center_widget)

        main_splitter = QSplitter(Qt.Horizontal)

        layout.addWidget(main_splitter)

        # file tree
        self.file_tree = C2FileTree(self)

        self.file_tree.openFile.connect(self.open_current_file)
        self.file_tree.translateFile.connect(self.translate_file)

        main_splitter.addWidget(self.file_tree)

        # self.file_tree.setStyleSheet(
        #     """
        #     QWidget {
        #         background-color: #3498db;
        #     }
        #     """
        # )

        right_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(right_splitter)

        # text editor
        self.text_editor = C2TextEditor(self)
        self.text_editor.dropFile.connect(
            self.drop_file
        )
        self.text_editor.newFile.connect(self.new_file)
        self.text_editor.saveFile.connect(self.save_file)
        self.text_editor.openFile.connect(self.open_file)

        right_splitter.addWidget(self.text_editor)

        # self.text_editor.setStyleSheet(
        #     """
        #     QWidget {
        #         background-color: #2ecc71;
        #     }
        #     """
        # )

        # console
        self.console = C2Console(self)

        self.console.commandEntered.connect(
            self.handle_command
        )

        right_splitter.addWidget(self.console)

        # self.console.setStyleSheet(
        #     """
        #     QWidget {
        #         background-color: #e74c3c;
        #     }
        #     """
        # )

        # set scale
        main_splitter.setSizes(
            [250, 900]
        )

        right_splitter.setSizes(
            [600, 300]
        )

    def init_menu_event(self):

        self.menu_bar.new_action.triggered.connect(
            self.new_file
        )

        self.menu_bar.open_action.triggered.connect(
            self.open_file
        )

        self.menu_bar.save_action.triggered.connect(
            self.save_file
        )

        self.menu_bar.save_as_action.triggered.connect(
            self.save_as_file
        )

        self.menu_bar.set_work_directory_action.triggered.connect(
            self.set_work_directory
        )

        self.menu_bar.close_action.triggered.connect(
            self.close
        )

    def drop_file(self, file_path):

        self.status_bar.set_message(
            file_path
        )

    def new_file(self):

        if self.text_editor.modified:

            result = QMessageBox.question(
                self,
                "Save File",
                "Current file has been modified. Save?",
                QMessageBox.Save |
                QMessageBox.Discard |
                QMessageBox.Cancel
            )

            if result == QMessageBox.Save:

                self.save_file()

            elif result == QMessageBox.Cancel:

                return

        self.text_editor.clear()

        self.text_editor.current_file = None

        msg = "Create New File"

        self.status_bar.set_message(msg)

        self.console.append_message(msg)

    def open_file(self):
        select_file = QFileDialog.getOpenFileName(
            self,
            "Select File"
        )

        file_path = select_file[0]

        if file_path:

            self.text_editor.open_file(file_path)

            msg = f"open file: {file_path}"

            self.status_bar.set_message(msg)

            self.console.append_message(msg)

    def open_current_file(self, file_path):
        if file_path:

            self.text_editor.open_file(file_path)

            msg = f"open file: {file_path}"

            self.status_bar.set_message(msg)

            self.console.append_message(msg)

    def save_file(self):

        path = self.text_editor.current_file

        if not path:
            self.save_as_file()

            return

        with open(
                path,
                "w",
                encoding="utf-8"
        ) as f:
            f.write(
                self.text_editor.toPlainText()
            )

        self.text_editor.modified = False

        msg = f"Saved: {path}"

        self.status_bar.set_message(msg)

        self.console.append_message(msg)

    def save_as_file(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Text (*.txt *.k *.key)"
        )

        if path:
            with open(
                    path,
                    "w",
                    encoding="utf-8"
            ) as f:
                f.write(
                    self.text_editor.toPlainText()
                )

            self.text_editor.current_file = path

            self.text_editor.modified = False

            msg = f"Saved: {path}"

            self.status_bar.set_message(msg)

            self.console.append_message(msg)

    def set_work_directory(self):

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Work Directory"
        )

        if directory:
            self.file_tree.set_directory(
                directory
            )

            msg = f"Work directory: {directory}"

            self.status_bar.set_message(msg)

            self.console.append_message(msg)

    def translate_file(self, file_path):

        material_mapping_file_path = r"C:\Users\jiand\PycharmProjects\circlecircle2\Test_Items\material_mapping.json"

        basename = os.path.basename(file_path)
        name, ext = os.path.splitext(basename)

        ext = ext.lower()

        dialog = SelectDialog(parent=self, ext=ext)

        if ext == ".key" or ext == ".k":
            if dialog.exec() == QDialog.Accepted:
                result = dialog.get_selection()
                selected_solver = result["solver"]
                selected_version = result["version"]

                # print(selected_solver, selected_version)
                fea_keywords_translator.translate(file_path=file_path,
                                                  solver1="lsdyna",
                                                  version1="12.0",
                                                  solver2=selected_solver,
                                                  version2=selected_version,
                                                  material_mapping=False,
                                                  material_mapping_file_path=material_mapping_file_path)

    def handle_command(self, command):

        command = command.strip().lower()

        if command == "-open":

            self.open_file()

        elif command == "-save":

            self.save_file()

        elif command == "-save as":

            self.save_as_file()

        elif command == "-set work directory":

            self.set_work_directory()

        elif command == "-close":

            self.close()

        elif command == "-help":

            self.console.append_message("""
Available commands:

-open; -save; -save as; -set work directory
-close
-help
"""
                                        )

        else:

            self.console.append_message(
                "[ERROR] Unknown command:"
                + command
            )


if __name__ == '__main__':
    app = C2App()

    main_window = MainWindow(app)

    main_window.show()

    app.exec()
