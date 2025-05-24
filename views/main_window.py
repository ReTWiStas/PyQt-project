import os
import shutil
import sqlite3

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QScrollArea, \
    QMessageBox, QLineEdit, QComboBox, QFileDialog
from PyQt6.QtGui import QFont, QPixmap


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Уютный ДОМ")
        self.setGeometry(100, 100, 800, 600)

        # Главный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

        # Левая панель (меню)
        self.left_panel = QFrame()
        self.left_panel.setLayout(QVBoxLayout())
        self.left_panel.setFixedWidth(200)
        self.main_layout.addWidget(self.left_panel)

        # Правая панель (контент)
        self.right_panel = QFrame()
        self.right_panel.setLayout(QVBoxLayout())
        self.main_layout.addWidget(self.right_panel)

        # Инициализация интерфейса
        self.init_menu()
        self.show_catalog()

    def init_menu(self):
        # Кнопки меню
        self.catalog_btn = QPushButton("Каталог")
        self.catalog_btn.clicked.connect(self.show_catalog)

        self.cart_btn = QPushButton("Корзина")
        self.cart_btn.clicked.connect(self.show_cart)

        self.orders_btn = QPushButton("Мои заказы")
        self.orders_btn.clicked.connect(self.show_orders)

        self.add_product_btn = QPushButton("Добавить товар")
        self.add_product_btn.clicked.connect(self.show_add_product)
        self.add_product_btn.setVisible(False)  # Только для продавцов

        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.clicked.connect(self.show_settings)

        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.clicked.connect(self.logout)

        # Добавляем кнопки в меню
        self.left_panel.layout().addWidget(self.catalog_btn)
        self.left_panel.layout().addWidget(self.cart_btn)
        self.left_panel.layout().addWidget(self.orders_btn)
        self.left_panel.layout().addWidget(self.add_product_btn)
        self.left_panel.layout().addWidget(self.settings_btn)
        self.left_panel.layout().addWidget(self.logout_btn)
        self.left_panel.layout().addStretch()

    def update_menu(self):
        # Показываем кнопку добавления товара только для продавцов
        if self.current_user and self.current_user['role'] == 'Продавец':
            self.add_product_btn.setVisible(True)
        else:
            self.add_product_btn.setVisible(False)

    def show_catalog(self, category_id=None):
        # Очищаем правую панель
        self.clear_right_panel()

        # Заголовок
        title = QLabel("Каталог товаров")
        title.setFont(QFont('Arial', 16))
        self.right_panel.layout().addWidget(title)

        # Получаем категории
        categories = self.db.get_categories(parent_id=category_id)

        if categories:
            # Отображаем подкатегории
            for cat_id, cat_name in categories:
                btn = QPushButton(cat_name)
                btn.clicked.connect(lambda _, cid=cat_id: self.show_catalog(cid))
                self.right_panel.layout().addWidget(btn)

        # Получаем товары в текущей категории
        products = self.db.get_products(category_id)

        if products:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)

            products_widget = QWidget()
            products_layout = QVBoxLayout(products_widget)

            for prod_id, name, price, description, image_path in products:
                product_frame = QFrame()
                product_frame.setFrameShape(QFrame.Shape.Box)
                product_layout = QHBoxLayout(product_frame)

                # Изображение товара
                if image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                    img_label = QLabel()
                    img_label.setPixmap(pixmap)
                    product_layout.addWidget(img_label)

                # Информация о товаре
                info_label = QLabel(f"{name}\nЦена: {price} руб.\n{description}")
                product_layout.addWidget(info_label)

                # Кнопка "Подробнее"
                details_btn = QPushButton("Подробнее")
                details_btn.clicked.connect(lambda _, pid=prod_id: self.show_product(pid))
                product_layout.addWidget(details_btn)

                products_layout.addWidget(product_frame)

            scroll.setWidget(products_widget)
            self.right_panel.layout().addWidget(scroll)

    def show_product(self, product_id):
        self.clear_right_panel()

        product = self.db.get_product(product_id)
        if not product:
            QMessageBox.warning(self, "Ошибка", "Товар не найден")
            self.show_catalog()
            return

        prod_id, name, price, description, image_path = product

        # Основная информация
        title = QLabel(name)
        title.setFont(QFont('Arial', 16))
        self.right_panel.layout().addWidget(title)

        # Изображение
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            self.right_panel.layout().addWidget(img_label)

        # Описание и цена
        self.right_panel.layout().addWidget(QLabel(f"Цена: {price} руб."))
        self.right_panel.layout().addWidget(QLabel(f"Описание: {description}"))

        # Поле для количества
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Количество")
        self.right_panel.layout().addWidget(self.quantity_input)

        # Кнопка "Добавить в корзину"
        add_to_cart_btn = QPushButton("Добавить в корзину")
        add_to_cart_btn.clicked.connect(lambda: self.add_to_cart(product_id))
        self.right_panel.layout().addWidget(add_to_cart_btn)

        # Кнопка "Назад"
        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.show_catalog)
        self.right_panel.layout().addWidget(back_btn)

    def add_to_cart(self, product_id):
        try:
            quantity = int(self.quantity_input.text())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное количество")
            return

        product = self.db.get_product(product_id)
        if product:
            total_price = product[2] * quantity
            self.db.add_to_cart(self.current_user['id'], product_id, quantity, total_price)
            QMessageBox.information(self, "Успех", "Товар добавлен в корзину")

    def show_cart(self):
        self.clear_right_panel()

        title = QLabel("Корзина")
        title.setFont(QFont('Arial', 16))
        self.right_panel.layout().addWidget(title)

        cart_items = self.db.get_cart_items(self.current_user['id'])

        if not cart_items:
            self.right_panel.layout().addWidget(QLabel("Ваша корзина пуста"))
            return

        total = 0
        for item_id, product_name, quantity, price, total_price in cart_items:
            item_frame = QFrame()
            item_layout = QHBoxLayout(item_frame)

            item_layout.addWidget(QLabel(f"{product_name} x{quantity}"))
            item_layout.addWidget(QLabel(f"{total_price} руб."))

            remove_btn = QPushButton("Удалить")
            remove_btn.clicked.connect(lambda _, iid=item_id: self.remove_from_cart(iid))
            item_layout.addWidget(remove_btn)

            self.right_panel.layout().addWidget(item_frame)
            total += total_price

        self.right_panel.layout().addWidget(QLabel(f"Итого: {total} руб."))

        checkout_btn = QPushButton("Оформить заказ")
        checkout_btn.clicked.connect(self.checkout)
        self.right_panel.layout().addWidget(checkout_btn)

    def remove_from_cart(self, item_id):
        self.db.remove_from_cart(item_id)
        self.show_cart()

    def checkout(self):
        self.db.checkout(self.current_user['id'])
        QMessageBox.information(self, "Успех", "Заказ оформлен")
        self.show_catalog()

    def show_orders(self):
        self.clear_right_panel()

        title = QLabel("Мои заказы")
        title.setFont(QFont('Arial', 16))
        self.right_panel.layout().addWidget(title)

        orders = self.db.get_orders(self.current_user['id'])

        if not orders:
            self.right_panel.layout().addWidget(QLabel("У вас нет заказов"))
            return

        for order_id, order_date, status, total in orders:
            order_frame = QFrame()
            order_layout = QVBoxLayout(order_frame)

            order_layout.addWidget(QLabel(f"Заказ #{order_id}"))
            order_layout.addWidget(QLabel(f"Дата: {order_date}"))
            order_layout.addWidget(QLabel(f"Статус: {status}"))
            order_layout.addWidget(QLabel(f"Сумма: {total} руб."))

            details_btn = QPushButton("Подробнее")
            details_btn.clicked.connect(lambda _, oid=order_id: self.show_order_details(oid))
            order_layout.addWidget(details_btn)

            self.right_panel.layout().addWidget(order_frame)

    def show_order_details(self, order_id):
        self.clear_right_panel()

        order = self.db.get_order(order_id)
        if not order:
            QMessageBox.warning(self, "Ошибка", "Заказ не найден")
            self.show_orders()
            return

        title = QLabel(f"Заказ #{order_id}")
        title.setFont(QFont('Arial', 16))
        self.right_panel.layout().addWidget(title)

        self.right_panel.layout().addWidget(QLabel(f"Дата: {order[1]}"))
        self.right_panel.layout().addWidget(QLabel(f"Статус: {order[2]}"))
        self.right_panel.layout().addWidget(QLabel(f"Сумма: {order[3]} руб."))

        items = self.db.get_order_items(order_id)
        for product_name, quantity, price in items:
            self.right_panel.layout().addWidget(QLabel(f"{product_name} - {quantity} x {price} руб."))

        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.show_orders)
        self.right_panel.layout().addWidget(back_btn)

    def show_add_product(self):
        self.clear_right_panel()

        title = QLabel("Добавить товар")
        title.setFont(QFont('Arial', 16))
        self.right_panel.layout().addWidget(title)

        form = QWidget()
        form_layout = QVBoxLayout(form)

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Название")

        self.product_price = QLineEdit()
        self.product_price.setPlaceholderText("Цена")

        self.product_desc = QLineEdit()
        self.product_desc.setPlaceholderText("Описание")

        self.product_image = QLineEdit()
        self.product_image.setPlaceholderText("Путь к изображению")

        self.browse_btn = QPushButton("Выбрать изображение")
        self.browse_btn.clicked.connect(self.browse_image)

        self.category_combo = QComboBox()
        categories = self.db.get_categories()
        for cat_id, cat_name in categories:
            self.category_combo.addItem(cat_name, cat_id)

        submit_btn = QPushButton("Добавить")
        submit_btn.clicked.connect(self.submit_product)

        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.show_catalog)

        form_layout.addWidget(QLabel("Название:"))
        form_layout.addWidget(self.product_name)
        form_layout.addWidget(QLabel("Цена:"))
        form_layout.addWidget(self.product_price)
        form_layout.addWidget(QLabel("Описание:"))
        form_layout.addWidget(self.product_desc)
        form_layout.addWidget(QLabel("Изображение:"))
        form_layout.addWidget(self.product_image)
        form_layout.addWidget(self.browse_btn)
        form_layout.addWidget(QLabel("Категория:"))
        form_layout.addWidget(self.category_combo)
        form_layout.addWidget(submit_btn)
        form_layout.addWidget(back_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)

        self.right_panel.layout().addWidget(scroll)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # Копируем изображение в папку data/images
            if not os.path.exists('data/images'):
                os.makedirs('data/images')

            new_path = f"data/images/{os.path.basename(file_path)}"
            shutil.copy(file_path, new_path)
            self.product_image.setText(new_path)

    def submit_product(self):
        name = self.product_name.text()
        price = self.product_price.text()
        description = self.product_desc.text()
        image_path = self.product_image.text()
        category_id = self.category_combo.currentData()

        if not all([name, price, description, category_id]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную цену")
            return

        try:
            self.db.add_product(name, price, description, image_path, category_id)
            QMessageBox.information(self, "Успех", "Товар добавлен")
            self.show_catalog()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Товар с таким названием уже существует")

    def show_settings(self):
        self.clear_right_panel()

        title = QLabel("Настройки")
        title.setFont(QFont('Arial', 16))
        self.right_panel.layout().addWidget(title)

        form = QWidget()
        form_layout = QVBoxLayout(form)

        self.settings_name = QLineEdit(self.current_user.get('name', ''))
        self.settings_name.setPlaceholderText("Имя")

        self.settings_phone = QLineEdit(self.current_user.get('phone', ''))
        self.settings_phone.setPlaceholderText("Телефон")

        self.settings_password = QLineEdit()
        self.settings_password.setPlaceholderText("Новый пароль")
        self.settings_password.setEchoMode(QLineEdit.EchoMode.Password)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_settings)

        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.show_catalog)

        form_layout.addWidget(QLabel("Имя:"))
        form_layout.addWidget(self.settings_name)
        form_layout.addWidget(QLabel("Телефон:"))
        form_layout.addWidget(self.settings_phone)
        form_layout.addWidget(QLabel("Пароль:"))
        form_layout.addWidget(self.settings_password)
        form_layout.addWidget(save_btn)
        form_layout.addWidget(back_btn)

        self.right_panel.layout().addWidget(form)

    def save_settings(self):
        name = self.settings_name.text()
        phone = self.settings_phone.text()
        password = self.settings_password.text()

        if not name or not phone:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return

        try:
            self.db.update_user(self.current_user['id'], name, phone, password)
            self.current_user['name'] = name
            self.current_user['phone'] = phone
            QMessageBox.information(self, "Успех", "Настройки сохранены")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким телефоном уже существует")

    def logout(self):
        self.current_user = None
        self.main_app.show_auth_window()

    def clear_right_panel(self):
        # Очищаем правую панель
        while self.right_panel.layout().count():
            item = self.right_panel.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()