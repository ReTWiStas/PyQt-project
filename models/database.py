import sqlite3
import os
from pathlib import Path
from utils.paths import resource_path


class Database:
    def __init__(self, db_path='data/database.db'):
        self.db_path = resource_path(db_path)
        self.conn = None
        self.connect()

    def connect(self):
        """Создает все необходимые папки для БД"""
        abs_path = Path(self.db_path)
        os.makedirs(abs_path.parent, exist_ok=True)  # Создаем папку data если нет

        self.conn = sqlite3.connect(str(abs_path))
        self.create_tables()
        self.initialize_data()

    def create_tables(self):
        """Создает все необходимые таблицы"""
        cursor = self.conn.cursor()

        # Таблица пользователей
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           phone
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password
                           TEXT
                           NOT
                           NULL,
                           role
                           TEXT
                           NOT
                           NULL,
                           name
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица категорий
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS categories
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           parent_id
                           INTEGER,
                           FOREIGN
                           KEY
                       (
                           parent_id
                       ) REFERENCES categories
                       (
                           id
                       )
                           )
                       ''')

        # Таблица товаров
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS products
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           price
                           REAL
                           NOT
                           NULL
                           CHECK
                       (
                           price
                           >=
                           0
                       ),
                           description TEXT NOT NULL,
                           image_path TEXT,
                           category_id INTEGER NOT NULL,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY
                       (
                           category_id
                       ) REFERENCES categories
                       (
                           id
                       )
                           )
                       ''')

        # Таблица заказов
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS orders
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           product_id
                           INTEGER
                           NOT
                           NULL,
                           quantity
                           INTEGER
                           NOT
                           NULL
                           CHECK
                       (
                           quantity >
                           0
                       ),
                           total_price REAL NOT NULL CHECK
                       (
                           total_price
                           >=
                           0
                       ),
                           status TEXT NOT NULL DEFAULT 'В корзине',
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       ),
                           FOREIGN KEY
                       (
                           product_id
                       ) REFERENCES products
                       (
                           id
                       )
                           )
                       ''')

        self.conn.commit()

    def initialize_data(self):
        """Заполняет БД начальными данными"""
        cursor = self.conn.cursor()

        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Добавляем тестового пользователя
            cursor.execute(
                "INSERT INTO users (phone, password, role, name) VALUES (?, ?, ?, ?)",
                ('+79161234567', 'password123', 'Продавец', 'Иван Иванов')
            )

            # Добавляем категории
            categories = [
                ('Одежда', None),
                ('Игры', None),
                ('Книги', None),
                ('Бытовые предметы', None),
                ('Мужское', 1),
                ('Женское', 1),
                ('Детское', 1),
                ('Компьютерные игры', 2),
                ('Настольные игры', 2),
                ('Роман', 3),
                ('Повесть', 3),
                ('Комедия', 3),
                ('Трагедия', 3),
                ('Фантастика', 3),
                ('Поэзия', 3),
                ('Детектив', 3)
            ]

            cursor.executemany(
                "INSERT INTO categories (name, parent_id) VALUES (?, ?)",
                categories
            )

            # Добавляем тестовые товары
            products = [
                ('Куртка KL', 11235, 'Стильная куртка для холодной погоды', None, 5),
                ('Шляпа MW', 799, 'Модная шляпа для любого сезона', None, 5),
                ('Носки UO', 599, 'Теплые и удобные носки', None, 5),
                ('Fortnite', 0, 'Популярная компьютерная игра', None, 8),
                ('Genshin Impact', 0, 'Ролевая компьютерная игра', None, 8),
                ('Война и мир', 299, 'Классический роман Льва Толстого', None, 10),
                ('Герой нашего времени', 599, 'Роман Михаила Лермонтова', None, 10),
                ('Утюг', 3000, 'Паровой утюг с вертикальным отпариванием', None, 4),
                ('Холодильник', 32000, 'Двухкамерный холодильник с No Frost', None, 4)
            ]

            cursor.executemany(
                "INSERT INTO products (name, price, description, image_path, category_id) VALUES (?, ?, ?, ?, ?)",
                products
            )

            self.conn.commit()

import sys
import os

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# При запуске проверяем и создаем БД
db_path = resource_path('data/database.db')
if not os.path.exists(db_path):
    os.makedirs('data', exist_ok=True)
    db = Database(db_path)

