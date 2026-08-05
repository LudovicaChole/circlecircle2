from PySide6.QtWidgets import QApplication, QMainWindow


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


if __name__ == '__main__':
    app = C2App()

    main_window = MainWindow(app)

    main_window.show()

    app.exec()
