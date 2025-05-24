from models.database import Database


class AuthController:
    def __init__(self, db):
        self.db = db

    def login(self, phone, password):
        # Логика авторизации
        user = self.db.get_user(phone)
        if user and user[2] == password:
            return user
        return None