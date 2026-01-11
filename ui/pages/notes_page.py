from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class NotesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.ui()

    
    def ui(self):
        label = QLabel("notes-page")
        layout = QVBoxLayout(self)
        layout.addWidget(label)

        self.setStyleSheet("background-color: rgb(0,0,0)")