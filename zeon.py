from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QDateTime
from product_tab import ProductTab
from sales_tab import SalesTab
from analysis_tab import AnalysisTab  # Подключение вкладки анализа

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Система учёта пекарни")
        self.resize(1000, 800)

        # Создание центрального виджета
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Создание вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(ProductTab(), "Учёт продукции")
        self.tab_widget.addTab(SalesTab(), "Продажи")
        self.tab_widget.addTab(AnalysisTab(), "Анализ продаж") 

        # Добавляем метку для текущего времени
        self.date_time_label = QLabel(self)
        self.date_time_label.setAlignment(Qt.AlignCenter)

        # Добавляем вкладки и метку в центральное виджет
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.date_time_label)

        # Обновление времени
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000)  # Обновлять каждый 1000 мс (1 секунда)

        self.update_date_time()

    def update_date_time(self):
        """Обновление текущей даты и времени в метке"""
        current_date_time = QDateTime.currentDateTime()
        self.date_time_label.setText(current_date_time.toString("yyyy-MM-dd HH:mm:ss"))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
