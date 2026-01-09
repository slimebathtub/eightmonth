from ui.main_window import MainWindow
import sys
from PySide6.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)    
    main = MainWindow()
    main.show()
    app.exec()