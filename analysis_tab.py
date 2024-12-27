from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem, QPushButton
import sqlite3
from PyQt5.QtCore import QDate

class AnalysisTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Поля для выбора диапазона дат
        form_layout = QFormLayout()
        self.start_date = QDateEdit(self)
        self.end_date = QDateEdit(self)

        # Устанавливаем дату по умолчанию на сегодня
        current_date = QDate.currentDate()
        self.start_date.setDate(current_date.addMonths(-1))  # По умолчанию месяц назад
        self.end_date.setDate(current_date)

        form_layout.addRow("С :", self.start_date)
        form_layout.addRow("До:", self.end_date)

        # Кнопка для отображения данных
        self.show_button = QPushButton("Показать продажи", self)
        self.show_button.clicked.connect(self.show_sales_data)
        
        # Таблица для отображения данных
        self.sales_table = QTableWidget(self)
        self.sales_table.setColumnCount(6)  # Дата, Категория, Продукт, Количество, Итоговая сумма, Итого
        self.sales_table.setHorizontalHeaderLabels(["Дата", "Категория", "Продукт", "Количество", "Итоговая сумма", "Итого"])

        # Добавляем компоненты в layout
        layout.addLayout(form_layout)
        layout.addWidget(self.show_button)
        layout.addWidget(self.sales_table)

    def show_sales_data(self):
        """Отобразить данные о продажах за выбранный период"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        # Получаем данные из базы данных
        conn = sqlite3.connect('zeon.db')
        cursor = conn.cursor()

        query = '''
        SELECT date, name_category, product_name, quantity, quantity * sale_price AS batch
        FROM Sales
        WHERE date BETWEEN ? AND ?
        ORDER BY date
        '''
        
        cursor.execute(query, (start_date, end_date))
        sales = cursor.fetchall()
        conn.close()

        # Заполнение таблицы
        self.sales_table.setRowCount(len(sales))
        total_sales = 0
        for i, sale in enumerate(sales):
            self.sales_table.setItem(i, 0, QTableWidgetItem(sale[0]))  # Дата
            self.sales_table.setItem(i, 1, QTableWidgetItem(sale[1]))  # Категория
            self.sales_table.setItem(i, 2, QTableWidgetItem(sale[2]))  # Продукт
            self.sales_table.setItem(i, 3, QTableWidgetItem(str(sale[3])))  # Количество
            self.sales_table.setItem(i, 4, QTableWidgetItem(str(sale[4])))  # Итоговая сумма (batch)
            
            total_sales += sale[4]  # Суммируем итоговые суммы

        # Добавляем строку с итоговой суммой
        self.sales_table.setRowCount(len(sales) + 1)
        self.sales_table.setItem(len(sales), 4, QTableWidgetItem("Итого"))
        self.sales_table.setItem(len(sales), 5, QTableWidgetItem(str(total_sales)))