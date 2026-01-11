from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class TodayPage(QWidget):
    def __init__(self):
        super().__init__()
        self.ui()

    
    def ui(self):
        label = QLabel("today-page")
        layout = QVBoxLayout(self)
        layout.addWidget(label)

        self.setStyleSheet("background-color: rgb(100,100,0)")