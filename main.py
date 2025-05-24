import sys
from PyQt5.QtWidgets import QApplication
from models.database import Database
from controllers.auth_controller import AuthController
from views.auth_window import AuthWindow
from utils.paths import resource_path


class EShopApp:
    def __init__(self):
        db_path = resource_path('data/database.db')
        self.db = Database(db_path)
        self.auth_controller = AuthController(self.db)
        self.init_ui()

    def init_ui(self):
        self.app = QApplication(sys.argv)
        self.auth_window = AuthWindow(self.auth_controller)
        self.auth_window.show()
        sys.exit(self.app.exec())


if __name__ == '__main__':
    app = EShopApp()