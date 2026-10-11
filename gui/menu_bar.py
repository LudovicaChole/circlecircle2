from PySide6.QtWidgets import QMenuBar, QMessageBox
from PySide6.QtCore import Qt


class C2MenuBar(QMenuBar):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.create_file_menu()

        self.create_material_menu()
        self.create_optimization_menu()

        self.create_setting_menu()
        self.create_nn_menu()

        self.create_help_menu()
        for action, shortcut in ((self.save_action, 'Ctrl+S'), (self.new_action, 'Ctrl+N'),
                                 (self.open_action, 'Ctrl+O'), (self.translate_action, 'Ctrl+E')):
            action.setShortcut(shortcut)
            action.setShortcutContext(Qt.WindowShortcut)


    def create_file_menu(self):

        file_menu = self.addMenu(
            "File"
        )

        self.new_action = file_menu.addAction(
            "New"
        )

        self.open_action = file_menu.addAction(
            "Open"
        )

        self.save_action = file_menu.addAction(
            "Save"
        )

        self.save_as_action = file_menu.addAction(
            "Save as"
        )

        self.translate_action = file_menu.addAction(
            "Translate"
        )

        self.set_work_directory_action = file_menu.addAction(
            "Set Work Directory"
        )

        file_menu.addSeparator()

        self.close_action = file_menu.addAction(
            "Close"
        )

    def create_optimization_menu(self):

        optimization_menu = self.addMenu(
            "Optimization"
        )

        optimize_action = optimization_menu.addAction(
            "Structure"
        )

        refine_action = optimization_menu.addAction(
            "Thickness Refine"
        )


        optimize_action.triggered.connect(lambda: self.developing('Structure'))
        refine_action.triggered.connect(lambda: self.developing('Thickness Refine'))

    def developing(self, name):
        QMessageBox.information(self, name, 'This feature is under development.')

    def create_material_menu(self):
        menu = self.addMenu('Material')
        menu.addAction('GISSMO', lambda: self.developing('GISSMO'))

    def create_setting_menu(self):

        setting_menu = self.addMenu(
            "Setting"
        )

        self.material_library_path_action = setting_menu.addAction('Material Library Path')
        self.unit_action = setting_menu.addAction('Unit')
        self.editor_settings_action = setting_menu.addAction('Editor')

        self.clear_fea_action = setting_menu.addAction('Clear FEA Result')
        self.towing_length_action = setting_menu.addAction('ABAQUS Translate')
        self.towing_template_action = self.towing_length_action

        self.license_action = setting_menu.addAction(
            "License"
        )

        self.device_action = setting_menu.addAction(
            "Device"
        )


    def create_nn_menu(self):
        menu = self.addMenu('NN')
        self.towing_hook_nn_action = menu.addAction('Towing Hook NN')
        self.towing_nn_action = menu.addAction('Towing Shape NN')
        menu.menuAction().setVisible(False)

    def create_help_menu(self):

        help_menu = self.addMenu(
            "Help"
        )

        self.documentation_action = help_menu.addAction(
            "Documentation"
        )

        self.contact_action = help_menu.addAction(
            "Contact"
        )
