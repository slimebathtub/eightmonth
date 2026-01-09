from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from ui.components.sidebar import SideBar
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test")
        self.resize(900,600)

        central = QWidget()
        # central.setStyleSheet("background: rgb(100,0,0);")

        layout = QHBoxLayout()
        sidebar = SideBar()

        contentWidget = QWidget()
        contentWidget.setStyleSheet("background-color: rgb(0,100,0);")

        layout.addWidget(sidebar)
        layout.addWidget(contentWidget)

        central.setLayout(layout)
        layout.setStretch(0, 1)
        layout.setStretch(1, 4)
        self.setCentralWidget(central)



