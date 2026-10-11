"""Application settings with the shared translation-window appearance."""
from pathlib import Path
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QComboBox, QCheckBox, QSpinBox,
                               QPlainTextEdit)
from core.fea.material_units import MODEL_UNITS
from utilities.app_paths import application_directory
from gui.settings_dialog import SettingsDialog


class MaterialLibraryDialog(SettingsDialog):
    def __init__(self, window):
        super().__init__(window, 'Material Library Path', 350)
        self.window = window
        self.profile = window.profile_settings
        group = self.group('Material library location')
        row = QHBoxLayout()
        self.path = QLineEdit(self.profile.preferences()['material_library_path'])
        self.path.setAccessibleName('Material library path')
        row.addWidget(self.path, 1)
        browse = QPushButton('Browse…')
        browse.clicked.connect(self.browse)
        row.addWidget(browse)
        group.addLayout(row)
        reset = QPushButton('Use Application Folder')
        reset.clicked.connect(lambda: self.path.setText(str(application_directory())))
        reset_row = QHBoxLayout()
        reset_row.addWidget(reset)
        reset_row.addStretch()
        group.addLayout(reset_row)
        self.hint(group, 'Choose the folder containing Material_Library, or select Material_Library directly. All solver subfolders are scanned for material templates.')
        self.resolved = self.hint(group, '')
        self.path.textChanged.connect(self.update_location)
        self.update_location()
        self.add_buttons()

    def library(self):
        value = self.path.text().strip()
        if not value:
            raise ValueError('Select a material library location.')
        root = Path(value).expanduser()
        return root, root if root.name.lower() == 'material_library' else root / 'Material_Library'

    def update_location(self):
        try:
            _, library = self.library()
            self.resolved.setText(f'Library: {library}')
        except ValueError:
            self.resolved.setText('Select a material library location.')

    def browse(self):
        value = QFileDialog.getExistingDirectory(self, 'Select material library location', self.path.text())
        if value:
            self.path.setText(value)

    def save_values(self):
        root, library = self.library()
        if not library.is_dir():
            raise ValueError(f'Material_Library was not found in {root}.')
        self.profile.save_preferences(material_library_path=str(root.resolve()))
        self.window.status_bar.set_message(f'Material library: {library.resolve()}')


class UnitDialog(SettingsDialog):
    def __init__(self, window):
        super().__init__(window, 'Unit', 300)
        self.window = window
        self.profile = window.profile_settings
        group = self.group('Model material units')
        row = QHBoxLayout()
        row.addWidget(QLabel('Unit system:'))
        self.units = QComboBox()
        self.units.addItems(MODEL_UNITS)
        self.units.setCurrentText(self.profile.preferences()['unit'])
        row.addWidget(self.units, 1)
        group.addLayout(row)
        self.hint(group, 'Choose the units used by your source model. Material library properties are converted to this unit system.')
        self.hint(group, 'kg = kilogram · T = metric tonne · mm = millimetre · ms = millisecond · mJ = millijoule')
        self.add_buttons()

    def save_values(self):
        value = self.units.currentText()
        self.profile.save_preferences(unit=value)
        self.window.status_bar.set_message(f'Material units: {value}')


class EditorDialog(SettingsDialog):
    def __init__(self, window):
        super().__init__(window, 'Editor', 430)
        self.window = window
        self.profile = window.profile_settings
        values = self.profile.preferences()
        group = self.group('Text appearance')
        self.wrap = QCheckBox('Automatic word wrap')
        self.wrap.setChecked(values['word_wrap'])
        group.addWidget(self.wrap)
        row = QHBoxLayout()
        row.addWidget(QLabel('Font size:'))
        self.size = QSpinBox()
        self.size.setRange(6, 48)
        self.size.setSuffix(' pt')
        self.size.setValue(values['font_size'])
        row.addWidget(self.size, 1)
        group.addLayout(row)
        self.hint(group, 'These settings apply to the editor after saving and are remembered for the next session.')
        preview_group = self.group('Preview')
        self.preview = QPlainTextEdit('*NODE\n       1         0.0         0.0         0.0\n$ Preview of the editor font size and automatic word wrap for longer lines.')
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(95)
        preview_group.addWidget(self.preview)
        self.wrap.toggled.connect(self.update_preview)
        self.size.valueChanged.connect(self.update_preview)
        self.update_preview()
        self.add_buttons()

    def update_preview(self):
        font = QFont(self.window.text_editor.font())
        font.setPointSize(self.size.value())
        self.preview.setFont(font)
        self.preview.setLineWrapMode(QPlainTextEdit.WidgetWidth if self.wrap.isChecked() else QPlainTextEdit.NoWrap)

    def save_values(self):
        self.profile.save_preferences(word_wrap=self.wrap.isChecked(), font_size=self.size.value())
        self.window.text_editor.apply_preferences(self.profile.preferences())
        self.window.status_bar.set_message('Editor settings saved.')


def configure_material_library(window):
    MaterialLibraryDialog(window).exec()


def configure_unit(window):
    UnitDialog(window).exec()


def configure_editor(window):
    EditorDialog(window).exec()
