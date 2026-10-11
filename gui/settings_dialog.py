"""Shared visual components for application settings windows."""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QLabel,
                               QDialogButtonBox, QMessageBox)

SETTINGS_STYLE = """
    QDialog { background: #f8fafc; }
    QGroupBox { background: white; border: 1px solid #cbd5e1;
                border-radius: 8px; margin-top: 10px; padding: 16px; }
    QGroupBox::title { subcontrol-origin: margin; left: 12px;
                      padding: 0 6px; font-weight: 600; }
    QLabel#SettingsHint, QLabel#TranslateHint { color: #64748b; }
    QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {
        min-height: 30px; padding: 3px 8px;
    }
    QPushButton { min-height: 30px; padding: 3px 14px; }
"""


class SettingsDialog(QDialog):
    def __init__(self, parent, title, height=330):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(660, height)
        self.setMinimumWidth(540)
        self.setStyleSheet(SETTINGS_STYLE)
        self.content_layout = QVBoxLayout(self)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)

    def group(self, title):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        self.content_layout.addWidget(group)
        return layout

    def hint(self, layout, text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setObjectName('SettingsHint')
        layout.addWidget(label)
        return label

    def add_buttons(self):
        self.content_layout.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        self.content_layout.addWidget(buttons)

    def save(self):
        try:
            self.save_values()
            self.accept()
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, self.windowTitle(), str(error))

    def save_values(self):
        raise NotImplementedError
