from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QSpinBox, QLineEdit, QPushButton, QDialog, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import QDateTime
import sqlite3

class SalesTab(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        # Кнопка для добавления продажи
        self.sale_button = QPushButton("Продажа", self)
        self.sale_button.clicked.connect(self.show_sale_form)
        layout.addWidget(self.sale_button)
        
        self.setLayout(layout)

    def show_sale_form(self):
        """Показать форму для продажи"""
        self.dialog = SaleFormDialog(self)
        if self.dialog.exec_() == QDialog.Accepted:
            sale_data = self.dialog.get_data()

            # Проверка на количество
            if sale_data['quantity'] > self.get_current_quantity(sale_data['category'], sale_data['product_name']):
                QMessageBox.warning(self, "Ошибка", "Недостаточно товара в наличии для продажи.")
                return

            self.insert_sale(sale_data)
            self.update_accounting(sale_data)  # Обновляем таблицу Accounting

    def get_current_quantity(self, category, product_name):
        """Получить текущее количество товара в Accounting"""
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()
        cursor.execute(''' 
        SELECT quantity_production FROM Accounting
        WHERE name_category = ? AND product_name = ?
        ''', (category, product_name))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

    def insert_sale(self, sale_data):
        """Вставка данных о продаже в таблицу Sales"""
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()

        # Вычисляем итоговую сумму продажи
        batch = sale_data['quantity'] * sale_data['price']

        query = '''
        INSERT INTO Sales (name_category, product_name, quantity, sale_price, date, batch)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (sale_data['category'], sale_data['product_name'], sale_data['quantity'], sale_data['price'], sale_data['date'], batch))
        conn.commit()
        conn.close()

    def update_accounting(self, sale_data):
        """Обновление данных в таблице Accounting после продажи"""
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()

        # Получаем текущее количество продукции в Accounting
        cursor.execute(''' 
        SELECT quantity_production FROM Accounting
        WHERE name_category = ? AND product_name = ?
        ''', (sale_data['category'], sale_data['product_name']))
        result = cursor.fetchone()

        if result:
            current_quantity = result[0]
            new_quantity = current_quantity - sale_data['quantity']

            if new_quantity > 0:
                # Обновляем таблицу Accounting
                cursor.execute('''
                UPDATE Accounting
                SET quantity_production = ?
                WHERE name_category = ? AND product_name = ?
                ''', (new_quantity, sale_data['category'], sale_data['product_name']))
            else:
                # Если количество товара стало равно нулю, удаляем его из Accounting
                cursor.execute('''
                DELETE FROM Accounting
                WHERE name_category = ? AND product_name = ?
                ''', (sale_data['category'], sale_data['product_name']))

            conn.commit()

        conn.close()


class SaleFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить продажу")

        # Layout для формы
        layout = QFormLayout(self)

        # Поля для данных
        self.category_input = QComboBox(self)
        self.product_input = QComboBox(self)
        self.quantity_input = QSpinBox(self)
        self.date_input = QLineEdit(self)
        self.date_input.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd"))
        self.date_input.setReadOnly(True)

        # Заполнение данных категорий
        self.categories = self.fetch_categories()
        self.category_input.addItems(self.categories)

        # Добавление полей в форму
        layout.addRow("Категория товара:", self.category_input)
        layout.addRow("Товар:", self.product_input)
        layout.addRow("Количество:", self.quantity_input)
        layout.addRow("Дата продажи:", self.date_input)

        # Кнопки для подтверждения и отмены
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        # Обновление продуктов при изменении категории
        self.category_input.currentIndexChanged.connect(self.update_products)
        self.update_products()

    def fetch_categories(self):
        """Загрузка категорий из базы данных"""
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name_category FROM Categories")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories

    def update_products(self):
        """Обновление списка продуктов на основе выбранной категории"""
        category = self.category_input.currentText()
        self.product_input.clear()
        self.product_input.setEnabled(False)

        # Загрузка продуктов для выбранной категории
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT product_name FROM Production
            WHERE name_category = ?
        ''', (category,))
        products = cursor.fetchall()

        if products:
            self.product_input.addItem("Выберите продукт")
            for product_name in products:
                self.product_input.addItem(product_name[0])
            self.product_input.setEnabled(True)

        conn.close()

        # Ограничение на количество товара (не больше, чем есть в наличии)
        self.update_quantity_limit()

    def update_quantity_limit(self):
        """Обновление лимита для поля 'Количество' в зависимости от доступного количества товара"""
        category = self.category_input.currentText()
        product_name = self.product_input.currentText()
        
        if not product_name:
            return

        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT quantity_production FROM Accounting
            WHERE name_category = ? AND product_name = ?
        ''', (category, product_name))
        result = cursor.fetchone()

        if result:
            max_quantity = result[0]
            self.quantity_input.setMaximum(max_quantity)

        conn.close()

    def get_data(self):
        """Получить данные из формы"""
        category = self.category_input.currentText()
        product_name = self.product_input.currentText()
        
        # Получение цены из базы данных
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT production_price FROM Production
            WHERE name_category = ? AND product_name = ?
        ''', (category, product_name))
        result = cursor.fetchone()
        price = result[0] if result else 0
        conn.close()

        return {
            'category': category,
            'product_name': product_name,
            'quantity': self.quantity_input.value(),
            'price': price,
            'date': self.date_input.text()
        }