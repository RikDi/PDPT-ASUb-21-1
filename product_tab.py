from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QFormLayout, QDialog, QDialogButtonBox, QLabel, QMessageBox
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QColor, QBrush
import sqlite3

class ProductTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Кнопка для добавления записи
        self.add_button = QPushButton("Добавить запись", self)
        self.add_button.clicked.connect(self.show_add_form)
        self.layout.addWidget(self.add_button)

        # Кнопка для обновления данных
        self.refresh_button = QPushButton("Обновить данные", self)
        self.refresh_button.clicked.connect(self.fetch_and_display_data)
        self.layout.addWidget(self.refresh_button)

        # Создаем контейнер для отображения категорий
        self.category_layout = QVBoxLayout()
        self.layout.addLayout(self.category_layout)

        # Отображение данных
        self.fetch_and_display_data()

    def fetch_and_display_data(self):
        """Получение и отображение данных из базы данных"""
        # Очистка предыдущих таблиц
        for i in reversed(range(self.category_layout.count())):
            widget = self.category_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Подключение к базе данных
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()

        # SQL запрос для получения данных
        query = '''
        SELECT a.name_category, a.id_note, a.product_name, a.date, a.time, a.quantity_production, p.production_price, a.batch
        FROM Accounting a
        JOIN Categories c ON a.name_category = c.name_category
        JOIN Production p ON a.product_name = p.product_name
        ORDER BY a.date DESC, a.time DESC;
        '''
        cursor.execute(query)
        data = cursor.fetchall()

        # Группировка данных по категориям
        categories_data = {}
        for row in data:
            category = row[0]
            if category not in categories_data:
                categories_data[category] = []
            categories_data[category].append(row)

        # Создание таблиц для каждой категории
        for category, rows in categories_data.items():
            self.create_category_table(category, rows)

        conn.close()

    def create_category_table(self, category, rows):
        """Создание таблицы для каждой категории и отображение её записей"""
        table = QTableWidget()
        table.setRowCount(len(rows))
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Категория", "Наименование", "Дата", "Время", "Кол-во, шт.", "Цена, руб.", "Общая партия, руб."])

        for row_index, row in enumerate(rows):
            table.setItem(row_index, 0, QTableWidgetItem(row[0]))  # Категория
            table.setItem(row_index, 1, QTableWidgetItem(row[2]))  # Наименование
            table.setItem(row_index, 2, QTableWidgetItem(row[3]))  # Дата
            table.setItem(row_index, 3, QTableWidgetItem(row[4]))  # Время
            table.setItem(row_index, 4, QTableWidgetItem(str(row[5])))  # Количество
            table.setItem(row_index, 5, QTableWidgetItem(str(row[6])))  # Цена
            table.setItem(row_index, 6, QTableWidgetItem(str(row[7])))  # Общая партия

            # Выделение строк старше 24 часов
            record_date = QDateTime.fromString(f"{row[3]} {row[4]}", "yyyy-MM-dd HH:mm")
            current_date = QDateTime.currentDateTime()
            diff = record_date.secsTo(current_date)
            if diff > 86400:  # Старше 24 часов
                for col in range(table.columnCount()):
                    table.item(row_index, col).setBackground(QBrush(QColor(255, 255, 0)))  # Желтое выделение

        category_label = QLabel(f"Категория: {category}")
        self.category_layout.addWidget(category_label)
        self.category_layout.addWidget(table)

    def show_add_form(self):
        """Показать форму для добавления новой записи"""
        self.dialog = AddRecordDialog(self)
        if self.dialog.exec() == QDialog.Accepted:
            data = self.dialog.get_data()
            self.insert_record(data)
            self.fetch_and_display_data()  # Обновить таблицу

    def insert_record(self, data):
        """Добавить новую запись в таблицу Accounting"""
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()

        query = '''
        INSERT INTO Accounting (name_category, product_name, date, time, quantity_production, production_price)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (data['category'], data['product_name'], data['date'], data['time'], data['quantity'], data['price']))
        conn.commit()
        conn.close()

        # Отображаем сообщение об успешном добавлении записи
        QMessageBox.information(self, "Успех!", "Запись успешно добавлена.")

class AddRecordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")

        self.layout = QFormLayout(self)

        self.categories = self.fetch_categories()
        
        self.category_input = QComboBox(self)
        self.category_input.addItems(self.categories)

        self.product_input = QComboBox(self)
        self.product_input.setEnabled(False)  # Пока категория не выбрана - выключена

        self.date_input = QLineEdit(self)
        self.date_input.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd"))
        self.date_input.setReadOnly(True)

        self.time_input = QLineEdit(self)
        self.time_input.setText(QDateTime.currentDateTime().toString("HH:mm"))
        self.time_input.setReadOnly(True)

        self.quantity_input = QSpinBox(self)
        self.quantity_input.setMinimum(1)

        # Добавляем элементы формы
        self.layout.addRow("Категория:", self.category_input)
        self.layout.addRow("Продукт:", self.product_input)
        self.layout.addRow("Дата:", self.date_input)
        self.layout.addRow("Время:", self.time_input)
        self.layout.addRow("Количество:", self.quantity_input)

        # Кнопки для формы
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.category_input.currentIndexChanged.connect(self.update_products)
        self.update_products()

    def fetch_categories(self):
        """Получение списка категорий из базы данных"""
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

        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()
        cursor.execute('''  
            SELECT product_name, production_price
            FROM Production
            WHERE name_category = ?
        ''', (category,))
        products = cursor.fetchall()

        if products:
            self.product_input.addItem("Выберите продукт")
            for product_name, price in products:
                self.product_input.addItem(product_name, price)
            self.product_input.setEnabled(True)

        conn.close()

    def get_data(self):
        """Получение данных из формы"""
        return {
            'category': self.category_input.currentText(),
            'product_name': self.product_input.currentText(),
            'date': self.date_input.text(),
            'time': self.time_input.text(),
            'quantity': self.quantity_input.value(),
            'price': self.product_input.currentData()  # Получаем цену выбранного продукта
        }
