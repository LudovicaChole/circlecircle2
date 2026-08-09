from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox
from gui.menu_bar import C2MenuBar
from gui.file_tree_bar import C2FileTree
from gui.status_bar import C2StatusBar
from gui.console_bar import C2Console
from gui.text_editor import C2TextEditor


class C2App(QApplication):
    def __init__(self):
        super().__init__()

        self.setObjectName("CircleCircle2")

        primary_screen = self.primaryScreen()

        available_geometry = primary_screen.availableGeometry()

        self.available_width = available_geometry.width()

        self.available_height = available_geometry.height()


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

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

        self.status_bar.set_message(
            "New File"
        )

    def open_file(self):
        select_file = QFileDialog.getOpenFileName(
            self,
            "Select File"
        )

        file_path = select_file[0]

        self.text_editor.open_file(file_path)

        self.status_bar.set_message(file_path)

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

        self.status_bar.set_message(
            f"Saved: {path}"
        )

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

            self.status_bar.set_message(
                path
            )

    def set_work_directory(self):

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Work Directory"
        )

        if directory:
            self.file_tree.set_directory(
                directory
            )

            self.status_bar.set_message(
                f"Work directory: {directory}"
            )

    def handle_command(self, command):

        print(command)

        if command.startswith("-open"):

            self.console.append_message(
                "[INFO] Opening file..."
            )

        elif command == "-close":

            self.close()

        elif command == "-help":

            self.console.append_message(
                """
                Available commands:
            
                -open filename
                -close
                -optimize
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
