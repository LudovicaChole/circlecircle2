from PySide6.QtWidgets import QStatusBar, QLabel


class C2StatusBar(QStatusBar):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.message_label = QLabel()

        self.addWidget(
            self.message_label
        )

        self.set_message(
            "CircleCircle2 -> Version: 1.0"
        )

    def set_message(self, message):

        self.message_label.setText(
            message
        )