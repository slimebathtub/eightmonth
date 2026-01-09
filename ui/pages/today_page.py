from PySide6.QtWidgets import QWidget

class Today_Page(QWidget):
    def __init__(self):
        super().__init__()
        self.ui()

    
    def ui(self):
        self.setStyleSheet("background-color: rgb(200,200,200)")
        