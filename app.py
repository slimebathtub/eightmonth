from ui.main_window import MainWindow
import sys
from PySide6.QtWidgets import QApplication
from data.db import init_db

if __name__ == '__main__':
    init_db()
    app = QApplication(sys.argv)    
    main = MainWindow()
    main.show()
    app.exec()