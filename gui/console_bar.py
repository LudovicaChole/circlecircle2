from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QTextCursor


class C2Console(QPlainTextEdit):

    commandEntered = Signal(str)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.init_ui()

    def init_ui(self):

        self.setStyleSheet(
            """
            QPlainTextEdit {

                background-color:#1e1e1e;

                color:#d4d4d4;

                font-family:Consolas;

                font-size:12px;

            }
            """
        )

        self.setPlaceholderText(
            "Enter command..."
        )

        self.prompt = "> "

        self.appendPlainText(
            "CircleCircle2 Console 1.0\n"
            "Python 3.10(default, Aug, 8, 2026, 14:54) [64 bit AMD64]\n"
            "Type ? for more help\n"
        )

        self.appendPlainText(
            self.prompt
        )

    def append_message(self, message):

        self.appendPlainText(
            message
        )

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Return:

            cursor = self.textCursor()

            cursor.movePosition(
                QTextCursor.StartOfLine
            )

            cursor.select(
                QTextCursor.LineUnderCursor
            )

            command = cursor.selectedText()

            command = command.replace(
                self.prompt,
                ""
            ).strip()

            if command:
                self.commandEntered.emit(
                    command
                )

            self.appendPlainText(
                self.prompt
            )

            return

        super().keyPressEvent(event)