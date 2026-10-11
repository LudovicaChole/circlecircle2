"""Folder/part labeling and cancellable background point-cloud training."""
from pathlib import Path
from PySide6.QtCore import QThread, Signal, Qt, QRect, QRectF, QEvent
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QFileDialog, QTableWidget, QTableWidgetItem, QSpinBox,
                               QMessageBox, QInputDialog, QCheckBox, QComboBox,
                               QDoubleSpinBox, QFormLayout, QLineEdit, QDialogButtonBox,
                               QGroupBox, QHeaderView, QStyledItemDelegate,
                               QStyleOptionViewItem, QStyle)
from utilities.logger import logger
from utilities import towing_settings


class Worker(QThread):
    result = Signal(object)
    failed = Signal(str)
    message = Signal(str)

    def __init__(self, operation, parent=None):
        super().__init__(parent)
        self.operation = operation

    def run(self):
        try:
            self.result.emit(self.operation(self))
        except Exception as error:
            self.failed.emit(str(error))


class TargetCheckDelegate(QStyledItemDelegate):
    """Keep checkbox rendering and hit targets consistent across Windows themes."""

    def indicator_rect(self, option, index):
        size = min(18, option.rect.height() - 4, option.rect.width() - 4)
        return QRect(option.rect.left() + 6,
                     option.rect.top() + (option.rect.height() - size) // 2, size, size)

    def paint(self, painter, option, index):
        rectangle = self.indicator_rect(option, index)
        background = QStyleOptionViewItem(option)
        self.initStyleOption(background, index)
        background.features &= ~QStyleOptionViewItem.HasCheckIndicator
        super().paint(painter, background, index)
        checked = index.data(Qt.CheckStateRole) == Qt.Checked.value
        enabled = bool(option.state & QStyle.State_Enabled)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        box = QRectF(rectangle.adjusted(1, 1, -1, -1))
        painter.setPen(QPen(QColor('#2563eb' if enabled else '#94a3b8'), 1))
        painter.setBrush(QColor('#2563eb' if checked and enabled else
                               '#94a3b8' if checked else '#ffffff'))
        painter.drawRoundedRect(box, 3, 3)
        if checked:
            check = QPainterPath()
            check.moveTo(box.left() + box.width() * .20, box.top() + box.height() * .52)
            check.lineTo(box.left() + box.width() * .43, box.top() + box.height() * .75)
            check.lineTo(box.left() + box.width() * .82, box.top() + box.height() * .27)
            painter.setPen(QPen(QColor('#ffffff'), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawPath(check)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if not (option.state & QStyle.State_Enabled and
                index.flags() & Qt.ItemIsEnabled and index.flags() & Qt.ItemIsUserCheckable):
            return False
        if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick, QEvent.MouseButtonRelease):
            if event.button() != Qt.LeftButton or not option.rect.contains(event.position().toPoint()):
                return False
            if event.type() != QEvent.MouseButtonRelease:
                return True
        elif event.type() == QEvent.KeyPress:
            if event.key() not in (Qt.Key_Space, Qt.Key_Select) or event.isAutoRepeat():
                return False
        else:
            return False
        checked = index.data(Qt.CheckStateRole) == Qt.Checked.value
        return model.setData(index, Qt.Unchecked.value if checked else Qt.Checked.value, Qt.CheckStateRole)


class TrainingDialog(QDialog):
    def __init__(self, kind, parent=None, license_manager=None):
        super().__init__(parent)
        from utilities.licensing import LicenseManager
        self.license_manager = license_manager or LicenseManager()
        self.kind, self.parts, self.worker = kind, [], None
        self.setWindowTitle('Towing Hook NN' if kind == 'hook' else 'Towing Shape NN')
        self.resize(900, 680)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        self.setStyleSheet('''
            QDialog { background: #f8fafc; }
            QGroupBox { font-weight: 600; border: 1px solid #cbd5e1;
                        border-radius: 8px; margin-top: 10px; padding: 14px; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
            QPushButton { min-height: 32px; padding: 3px 16px; border-radius: 6px;
                          border: 1px solid #cbd5e1; background: #ffffff; color: #334155; }
            QPushButton:hover { background: #e2e8f0; }
            QPushButton:focus { border: 2px solid #2563eb; }
            QPushButton#TrainButton { background: #15803d; border-color: #15803d; color: white; font-weight: 600; }
            QPushButton#TrainButton:hover { background: #166534; }
            QPushButton#CancelButton { background: #dc2626; border-color: #dc2626; color: white; font-weight: 600; }
            QPushButton#CancelButton:hover { background: #b91c1c; }
            QPushButton#ValidateButton { background: #facc15; border-color: #eab308; color: #422006; font-weight: 600; }
            QPushButton#ValidateButton:hover { background: #eab308; }
            QPushButton:disabled { background: #e2e8f0; border-color: #cbd5e1; color: #94a3b8; }
            QPushButton#TrainButton:disabled { background: #dcfce7; border-color: #bbf7d0; color: #6b8f77; }
            QPushButton#CancelButton:disabled { background: #fee2e2; border-color: #fecaca; color: #a77878; }
            QPushButton#ValidateButton:disabled { background: #fef9c3; border-color: #fde68a; color: #a39460; }
            QSpinBox, QDoubleSpinBox, QComboBox { min-height: 28px; }
            QTableWidget { background: white; border: 1px solid #cbd5e1; border-radius: 6px; }
            QLabel#TrainingStatus { background: #eff6ff; color: #334155; border-radius: 6px; padding: 10px; }
        ''')
        self.type_select = QComboBox()
        self.type_select.addItem('Towing Hook NN', 'hook')
        self.type_select.addItem('Towing Shape NN', 'towing')
        self.type_select.setCurrentIndex(0 if kind == 'hook' else 1)
        self.type_select.currentIndexChanged.connect(self.change_kind)
        header = QHBoxLayout()
        header.addWidget(QLabel('Model type:'))
        header.addWidget(self.type_select, 1)
        layout.addLayout(header)
        hint = QLabel('Filename labels: 1008.k marks PART 1008 as target; other parts are background.\n'
                      'Multiple targets: 1008_1009.k. Use background.k for background-only files.')
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self.filename_labels = QCheckBox('Automatically label target PARTs from K filenames')
        self.filename_labels.setChecked(True)
        self.filename_labels.toggled.connect(self.clear_parts)
        self.choose = QPushButton('Choose Training Folder')
        self.choose.clicked.connect(self.choose_folder)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.filename_labels)
        folder_row.addStretch()
        folder_row.addWidget(self.choose)
        layout.addLayout(folder_row)
        self.table = QTableWidget(0,3)
        self.table.setItemDelegateForColumn(0, TargetCheckDelegate(self.table))
        self.table.setHorizontalHeaderLabels(['Target', 'File / PART', 'Nodes'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)
        training_group = QGroupBox('Training parameters')
        row = QHBoxLayout(training_group)
        row.addWidget(QLabel('Epochs:'))
        self.epochs = QSpinBox()
        self.epochs.setRange(1,10000)
        self.epochs.setValue(100)
        row.addWidget(self.epochs)
        self.learning_rate = QDoubleSpinBox()
        self.learning_rate.setDecimals(6)
        self.learning_rate.setRange(.000001, 1)
        self.learning_rate.setValue(.001)
        row.addWidget(QLabel('Learning rate:'))
        row.addWidget(self.learning_rate)
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 512)
        self.batch_size.setValue(8)
        row.addWidget(QLabel('Batch size:'))
        row.addWidget(self.batch_size)
        layout.addWidget(training_group)
        self.start = QPushButton('Train')
        self.start.setObjectName('TrainButton')
        self.start.setMinimumWidth(120)
        self.start.clicked.connect(self.train)
        self.cancel = QPushButton('Cancel Training')
        self.cancel.setObjectName('CancelButton')
        self.cancel.clicked.connect(self.cancel_training)
        validation_group = QGroupBox('Validation acceptance criteria')
        criteria = QHBoxLayout(validation_group)
        self.minimum_precision = QDoubleSpinBox()
        self.minimum_recall = QDoubleSpinBox()
        for title, field in (('Minimum validation precision:', self.minimum_precision),
                             ('Minimum validation recall:', self.minimum_recall)):
            field.setRange(0, 1)
            field.setSingleStep(.01)
            field.setValue(.9)
            criteria.addWidget(QLabel(title))
            criteria.addWidget(field)
        layout.addWidget(validation_group)
        self.validation = QPushButton('Validate Model')
        self.validation.setObjectName('ValidateButton')
        self.validation.setToolTip('Evaluate the saved model on a separate labeled folder.')
        self.validation.clicked.connect(self.validate_model)
        actions = QHBoxLayout()
        actions.setSpacing(12)
        for button in (self.start, self.cancel, self.validation):
            actions.addWidget(button)
        actions.addStretch()
        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close)
        actions.addWidget(self.close_button)
        layout.addLayout(actions)
        self.status = QLabel('No folder selected.')
        self.status.setObjectName('TrainingStatus')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.set_busy(False)

    def set_busy(self, busy):
        for widget in (self.type_select, self.learning_rate, self.batch_size, self.validation,
                       self.minimum_precision, self.minimum_recall):
            widget.setEnabled(not busy)
        self.choose.setEnabled(not busy)
        self.filename_labels.setEnabled(not busy)
        self.start.setEnabled(not busy and bool(self.parts))
        self.table.setEnabled(not busy)
        self.epochs.setEnabled(not busy)
        self.cancel.setEnabled(busy)

    def dispatch(self, operation, callback):
        self.worker = Worker(operation, self)
        self.worker.result.connect(callback)
        self.worker.message.connect(self.report)
        self.worker.failed.connect(self.failure)
        self.worker.finished.connect(self.worker_finished)
        self.set_busy(True)
        self.worker.start()

    def report(self, message):
        self.status.setText(message)
        logger.info(message)

    def failure(self, message):
        self.status.setText(message)
        logger.warning(message)
        QMessageBox.warning(self, 'Towing NN', message)

    def worker_finished(self):
        worker, self.worker = self.worker, None
        worker.deleteLater()
        self.set_busy(False)

    def choose_folder(self):
        if not self.require_activation():
            return
        folder = QFileDialog.getExistingDirectory(self, 'Select training folder')
        if not folder:
            return
        automatic = self.filename_labels.isChecked()
        self.clear_parts()
        def read(worker):
            from core.nn.towing_data import folder_parts
            worker.message.emit('Reading training mesh parts...')
            return folder_parts(folder, worker.isInterruptionRequested,
                                filename_labels=automatic, progress=worker.message.emit)
        self.dispatch(read, self.loaded)

    def clear_parts(self):
        self.parts = []
        self.table.setRowCount(0)
        self.start.setEnabled(False)
        self.status.setText('Select a training folder. Reload after changing the labeling mode.')

    def loaded(self, parts):
        self.parts = parts
        self.table.setRowCount(len(parts))
        for row, part in enumerate(parts):
            target = QTableWidgetItem()
            target.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            target.setCheckState(Qt.Checked if part.target else Qt.Unchecked)
            self.table.setItem(row,0,target)
            for column, value in ((1, f'{part.source} / PART {part.pid}'), (2,str(len(part.points)))):
                item = QTableWidgetItem(value)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(row,column,item)
        if all(part.target is not None for part in parts):
            targets = sum(bool(part.target) for part in parts)
            self.status.setText(f'Labels ready: {targets} targets, {len(parts)-targets} backgrounds. Click Train.')
        else:
            self.status.setText(f'{len(parts)} parts loaded. Select target parts, then Train.')

    def train(self):
        if not self.require_activation():
            return
        labels = [int(self.table.item(i,0).checkState() == Qt.Checked) for i in range(len(self.parts))]
        if set(labels) != {0,1}:
            QMessageBox.warning(self, 'Training Labels', 'Both target and background parts are required.\n'
                                'Check filename labels or add background.k.\n'
                                'In manual mode, check targets and leave backgrounds unchecked.')
            return
        epochs, parts, kind = self.epochs.value(), list(self.parts), self.kind
        rate, batch = self.learning_rate.value(), self.batch_size.value()
        def run(worker):
            from core.nn.towing_pointnet import train
            return train(parts, labels, kind, epochs, worker.message.emit, worker.isInterruptionRequested,
                         learning_rate=rate, batch_size=batch)
        self.dispatch(run, lambda path: self.report(f'Model saved: {path}. Click Validate Model to evaluate separate files.'))

    def change_kind(self):
        self.kind = self.type_select.currentData()
        self.setWindowTitle(self.type_select.currentText())

    def validate_model(self):
        if not self.require_activation():
            return
        folder = QFileDialog.getExistingDirectory(self, 'Select independently labeled validation folder')
        if not folder:
            return
        kind = self.kind
        precision, recall = self.minimum_precision.value(), self.minimum_recall.value()
        def run(worker):
            from core.nn.towing_data import folder_parts
            from core.nn.towing_pointnet import validate
            parts = folder_parts(folder, worker.isInterruptionRequested, True, worker.message.emit)
            return validate(parts, kind, progress=worker.message.emit,
                            cancelled=worker.isInterruptionRequested,
                            minimum_precision=precision, minimum_recall=recall)
        self.dispatch(run, lambda report: self.report(report))

    def require_activation(self):
        status = self.license_manager.status()
        if status.valid:
            return True
        message = 'Activate the software in Setting > License to use NN training and validation.\n' + status.message
        self.status.setText(message)
        QMessageBox.warning(self, 'Activation Required', message)
        return False

    def cancel_training(self):
        if self.worker:
            self.worker.requestInterruption()
            self.status.setText('Cancellation requested. Waiting for current operation...')

    def reject(self):
        if self.worker:
            self.cancel_training()
            return
        super().reject()

    def closeEvent(self,event):
        if self.worker:
            self.cancel_training()
            event.ignore()
        else:
            super().closeEvent(event)


def configure_length(window):
    try:
        settings = towing_settings.load()
        value, accepted = QInputDialog.getDouble(window, 'Towing L',
            'Signed length L (model units; + / - selects opposite aligned end faces):',
            settings['length'], -1e6,1e6, 6)
        if accepted:
            settings['length'] = value
            towing_settings.save(settings)
    except (OSError,ValueError) as error:
        QMessageBox.warning(window,'Towing L',str(error))


def configure_translation(window):
    try:
        settings = towing_settings.load()
        dialog = QDialog(window)
        dialog.setWindowTitle('ABAQUS Translate')
        dialog.resize(660, 430)
        from gui.settings_dialog import SETTINGS_STYLE
        dialog.setStyleSheet(SETTINGS_STYLE)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        generated_group = QGroupBox('Generated towing hook')
        generated_layout = QVBoxLayout(generated_group)
        length_row = QHBoxLayout()
        length = QDoubleSpinBox()
        length.setDecimals(6)
        length.setRange(-1e6, 1e6)
        length.setValue(settings['length'])
        length.setToolTip('Length of the generated towing hook in model units. The sign selects the aligned end face.')
        length_row.addWidget(QLabel('Towing L:'))
        length_row.addWidget(length, 1)
        generated_layout.addLayout(length_row)
        length_hint = QLabel('Generated hook length in model units. Positive / negative L selects the aligned end face.')
        length_hint.setObjectName('TranslateHint')
        length_hint.setWordWrap(True)
        generated_layout.addWidget(length_hint)
        layout.addWidget(generated_group)
        model_group = QGroupBox('Towing Model Select')
        model_layout = QVBoxLayout(model_group)
        template = QLineEdit(settings['template'])
        template.setPlaceholderText('No model selected — use generated hook')
        template.setAccessibleName('Towing model file')
        model_row = QHBoxLayout()
        model_row.addWidget(template, 1)
        browse = QPushButton('Browse…')
        browse.setToolTip('Choose an existing towing hook mesh (INP / GEO).')
        def choose():
            path, _ = QFileDialog.getOpenFileName(dialog, 'Select towing model', template.text(), 'Abaqus mesh (*.inp *.geo)')
            if path:
                template.setText(path)
        browse.clicked.connect(choose)
        model_row.addWidget(browse)
        model_layout.addLayout(model_row)
        generated = QPushButton('Use Generated Hook')
        generated.clicked.connect(template.clear)
        reset_row = QHBoxLayout()
        reset_row.addWidget(generated)
        reset_row.addStretch()
        model_layout.addLayout(reset_row)
        note = QLabel('Empty model selection generates a cylinder. Existing templates preserve shape, material and length; L selects direction.')
        note.setWordWrap(True)
        note.setObjectName('TranslateHint')
        model_layout.addWidget(note)
        layout.addWidget(model_group)
        layout.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        def save():
            try:
                settings.update(length=length.value(), template=template.text().strip())
                if settings['template'] and not Path(settings['template']).is_file():
                    raise ValueError('The selected towing model does not exist.')
                towing_settings.save(settings)
                dialog.accept()
            except (OSError, ValueError) as error:
                QMessageBox.warning(dialog, 'ABAQUS Translate', str(error))
        buttons.accepted.connect(save)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()
    except (OSError, ValueError) as error:
        QMessageBox.warning(window, 'ABAQUS Translate', str(error))


def configure_template(window):
    try:
        settings = towing_settings.load()
        dialog = QMessageBox(window)
        dialog.setWindowTitle('Towing Model')
        dialog.setText('Choose an Abaqus solid mesh template, or use the generated cylinder.\n'
                       'Template shape/material/length are preserved; the sign of L selects direction.')
        choose = dialog.addButton('Choose INP / GEO', QMessageBox.ActionRole)
        generated = dialog.addButton('Generated Cylinder', QMessageBox.ActionRole)
        dialog.addButton(QMessageBox.Cancel)
        dialog.exec()
        if dialog.clickedButton() is choose:
            path, _ = QFileDialog.getOpenFileName(window,'Towing solid mesh template',settings['template'],
                                                'Abaqus mesh (*.inp *.geo)')
            if not path:
                return
            settings['template'] = str(Path(path).resolve())
        elif dialog.clickedButton() is generated:
            settings['template'] = ''
        else:
            return
        towing_settings.save(settings)
    except (OSError,ValueError) as error:
        QMessageBox.warning(window,'Towing Model',str(error))
