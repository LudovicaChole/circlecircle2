"""Developer-only license generator; excluded from the application by pack.py.

Run from the source project. Keep config/private_key.pem here;
distributed applications use only config/public_key.pem to verify codes.
"""
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QComboBox,
                               QSpinBox, QPlainTextEdit, QPushButton, QLabel, QMessageBox,
                               QVBoxLayout, QHBoxLayout, QGroupBox)
from utilities.error_messages import error_message
from utilities.license_issuer import issue_license
from utilities.device_info import local_ipv4_addresses


class LicenseGenerator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('CircleCircle2 — License Generator')
        self.resize(680, 540)
        self.setStyleSheet('''
            QDialog { background: #f8fafc; }
            QGroupBox { background: white; border: 1px solid #cbd5e1; border-radius: 8px;
                        margin-top: 10px; padding: 16px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; font-weight: 600; }
            QLabel#GeneratorHint { color: #64748b; }
            QComboBox, QSpinBox { min-height: 30px; padding: 3px 8px; }
            QPlainTextEdit { background: #ffffff; border: 1px solid #cbd5e1;
                             border-radius: 6px; padding: 10px; }
            QPushButton { min-height: 32px; padding: 3px 16px; border: 1px solid #cbd5e1;
                          border-radius: 6px; background: white; color: #334155; }
            QPushButton:hover { background: #eff6ff; }
            QPushButton#GenerateLicense { background: #15803d; border-color: #15803d;
                                         color: white; font-weight: 600; }
            QPushButton#GenerateLicense:hover { background: #166534; }
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        settings = QGroupBox('License details')
        form = QFormLayout(settings)
        form.setSpacing(12)
        self.ipv4 = QComboBox()
        self.ipv4.setEditable(True)
        self.ipv4.setInsertPolicy(QComboBox.NoInsert)
        self.ipv4.addItems(local_ipv4_addresses())
        self.ipv4.lineEdit().setPlaceholderText('Enter an IPv4 address')
        self.ipv4.setToolTip('Defaults to a local IPv4 address; select or type another address.')
        form.addRow('License IPv4:', self.ipv4)
        self.days = QSpinBox()
        self.days.setRange(1, 36500)
        self.days.setValue(10)
        form.addRow('Valid days:', self.days)
        validity_hint = QLabel('Select or enter the target IPv4. Validity starts when the code is generated.')
        validity_hint.setObjectName('GeneratorHint')
        validity_hint.setWordWrap(True)
        form.addRow(validity_hint)
        layout.addWidget(settings)
        self.generate_button = QPushButton('Generate License')
        self.generate_button.setObjectName('GenerateLicense')
        self.generate_button.clicked.connect(self.generate)
        actions = QHBoxLayout()
        actions.addWidget(self.generate_button)
        keys = QPushButton('Generate Public / Private Keys')
        keys.clicked.connect(self.generate_keys)
        actions.addStretch()
        actions.addWidget(keys)
        layout.addLayout(actions)
        output = QGroupBox('Activation code')
        output_layout = QVBoxLayout(output)
        self.code = QPlainTextEdit()
        self.code.setReadOnly(True)
        self.code.setPlaceholderText('The activation code will appear here.')
        output_layout.addWidget(self.code, 1)
        copy = QPushButton('Copy Code')
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.code.toPlainText()))
        copy_row = QHBoxLayout()
        copy_row.addStretch()
        copy_row.addWidget(copy)
        output_layout.addLayout(copy_row)
        layout.addWidget(output, 1)
        note = QLabel('Paste the code into Setting → License in CircleCircle2.\n'
                      'The entered IPv4 must remain assigned to the computer using the license.')
        note.setWordWrap(True)
        note.setObjectName('GeneratorHint')
        layout.addWidget(note)

    def generate(self):
        try:
            self.code.setPlainText(issue_license(self.ipv4.currentText().strip(), self.days.value()))
        except Exception as error:
            QMessageBox.warning(self, 'Cannot Generate License', error_message(error))

    def generate_keys(self):
        from utilities.license_issuer import signing_key, PRIVATE_KEY_PATH, PUBLIC_KEY_PATH
        try:
            signing_key()
            QMessageBox.information(self, 'Keys Ready',
                f'Private key: {PRIVATE_KEY_PATH}\nPublic key: {PUBLIC_KEY_PATH}\n'
                'Existing keys are reused. Back up the private key.')
        except Exception as error:
            QMessageBox.warning(self, 'Cannot Generate Keys', error_message(error))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LicenseGenerator()
    window.show()
    sys.exit(app.exec())
