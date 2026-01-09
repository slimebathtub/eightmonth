from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class SideBar(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: rgb(0,0,100)")

        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(12)

        layout.addWidget(QPushButton("Today"))
        layout.addWidget(QPushButton("Notes"))
        layout.addWidget(QPushButton("Plan"))
        layout.addWidget(QPushButton("Tasks"))

        layout.addStretch()

        layout.addWidget(QPushButton("Setting"))

        self.setLayout(layout)

