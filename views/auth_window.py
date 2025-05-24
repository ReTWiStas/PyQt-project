import sqlite3

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt6.QtGui import QFont


class AuthWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self.login)

        self.register_btn = QPushButton("Регистрация")
        self.register_btn.clicked.connect(self.show_register)

        layout.addWidget(QLabel("Авторизация"))
        layout.addWidget(self.phone_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def login(self):
        phone = self.phone_input.text()
        password = self.password_input.text()

        if not phone or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        user = self.main_app.db.get_user(phone)
        if user and user[2] == password:
            self.main_app.current_user = {
                'id': user[0],
                'phone': user[1],
                'role': user[3],
                'name': user[4]
            }
            self.main_app.show_main_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный телефон или пароль")

    def show_register(self):
        self.main_app.stacked_widget.setCurrentIndex(1)


class RegisterWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["Покупатель", "Продавец"])

        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.register)

        self.back_btn = QPushButton("Назад")
        self.back_btn.clicked.connect(lambda: self.main_app.stacked_widget.setCurrentIndex(0))

        layout.addWidget(QLabel("Регистрация"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.role_combo)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.back_btn)

        self.setLayout(layout)

    def register(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()

        if not all([name, phone, password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            self.main_app.db.add_user(name, phone, password, role)
            QMessageBox.information(self, "Успех", "Регистрация завершена")
            self.main_app.stacked_widget.setCurrentIndex(0)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким телефоном уже существует")
