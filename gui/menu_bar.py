from PySide6.QtWidgets import QMenuBar


class C2MenuBar(QMenuBar):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.create_file_menu()

        self.create_optimization_menu()

        self.create_setting_menu()

        self.create_help_menu()


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

        self.export_action = file_menu.addAction(
            "Export"
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
            "Optimize"
        )

        refine_action = optimization_menu.addAction(
            "Refine"
        )


    def create_setting_menu(self):

        setting_menu = self.addMenu(
            "Setting"
        )

        license_action = setting_menu.addAction(
            "License"
        )

        device_action = setting_menu.addAction(
            "Device"
        )


    def create_help_menu(self):

        help_menu = self.addMenu(
            "Help"
        )

        documentation_action = help_menu.addAction(
            "Documentation"
        )

        contact_action = help_menu.addAction(
            "Contact"
        )