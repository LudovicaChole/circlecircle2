from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPlainTextEdit, QPushButton, QDialogButtonBox, QGroupBox)
from utilities.error_messages import error_message
from utilities.licensing import LicenseManager
from utilities.device_info import local_ipv4_addresses
from utilities.logger import logger


class LicenseDialog(QDialog):
    def __init__(self, manager=None, parent=None):
        super().__init__(parent)
        self.manager = manager or LicenseManager()
        self.setWindowTitle('CircleCircle2 — License')
        self.resize(640, 500)
        self.setStyleSheet('''
            QDialog { background: #f8fafc; }
            QGroupBox { background: white; border: 1px solid #cbd5e1; border-radius: 8px;
                        margin-top: 10px; padding: 16px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; font-weight: 600; }
            QLabel#LicenseBadge { border-radius: 6px; padding: 6px 14px; font-weight: 600; }
            QLabel#LicenseHint { color: #64748b; }
            QPlainTextEdit { background: #ffffff; border: 1px solid #cbd5e1;
                             border-radius: 6px; padding: 10px; }
            QPlainTextEdit:focus { border-color: #60a5fa; }
            QPushButton { min-height: 32px; padding: 3px 18px; }
            QPushButton#ActivateButton { background: #15803d; color: white;
                                        border: 1px solid #15803d; border-radius: 6px; font-weight: 600; }
            QPushButton#ActivateButton:hover { background: #166534; }
        ''')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        status_group = QGroupBox('License status')
        status_layout = QVBoxLayout(status_group)
        self.badge = QLabel()
        self.badge.setObjectName('LicenseBadge')
        badge_row = QHBoxLayout()
        badge_row.addWidget(self.badge)
        badge_row.addStretch()
        status_layout.addLayout(badge_row)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        status_layout.addWidget(self.status_label)
        layout.addWidget(status_group)
        activation_group = QGroupBox('Activation code')
        activation_layout = QVBoxLayout(activation_group)
        hint = QLabel('Paste your code below, then click Activate.')
        hint.setObjectName('LicenseHint')
        activation_layout.addWidget(hint)
        self.code = QPlainTextEdit()
        self.code.setPlaceholderText('Paste your activation code here')
        activation_layout.addWidget(self.code, 1)
        layout.addWidget(activation_group, 1)
        activate = QPushButton('Activate')
        activate.setObjectName('ActivateButton')
        activate.setMinimumWidth(120)
        activate.clicked.connect(self.activate)
        close = QDialogButtonBox(QDialogButtonBox.Close)
        close.rejected.connect(self.reject)
        actions = QHBoxLayout()
        actions.addWidget(activate)
        actions.addStretch()
        actions.addWidget(close)
        layout.addLayout(actions)
        self.refresh(log_invalid=True)

    def refresh(self, status=None, log_invalid=False):
        status = status or self.manager.status()
        self.badge.setText('Active' if status.valid else 'Unavailable')
        self.badge.setStyleSheet('background: #dcfce7; color: #166534;' if status.valid
                                else 'background: #fff7ed; color: #9a3412;')
        lines = ['Status: ' + ('Valid' if status.valid else 'Unavailable'), status.message,
                 'Current IPv4: ' + (', '.join(local_ipv4_addresses()) or 'unavailable')]
        if status.ipv4:
            lines.append('Licensed IPv4: ' + status.ipv4)
        if status.expires_at:
            lines.append('Expires: ' + status.expires_at)
        self.status_label.setText('\n'.join(lines))
        if not status.valid and log_invalid:
            logger.warning('License unavailable. Please activate the software. ' + status.message)

    def activate(self):
        try:
            status = self.manager.activate(self.code.toPlainText())
            self.refresh(status, log_invalid=True)
            if status.valid:
                binding = f' IPv4: {status.ipv4};' if status.ipv4 else ''
                logger.info(f'Software activated successfully.{binding} Expires: {status.expires_at}')
                self.code.clear()
        except OSError as error:
            self.status_label.setText(f'Cannot save activation: {error_message(error)}')
            logger.error(f'Cannot save activation: {error_message(error)}')
