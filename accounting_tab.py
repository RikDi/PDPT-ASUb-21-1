from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class AccountingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Учет продукции"))
