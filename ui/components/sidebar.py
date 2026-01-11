from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class SideBar(QWidget):
    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: rgb(0,0,100)")

        layout = QVBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(12)

        btn_today = QPushButton("Today")
        btn_notes = QPushButton("Notes")
        btn_future = QPushButton("Future")
        btn_tasks = QPushButton("Tasks")

        btn_notes.clicked.connect(lambda: self.page_changed.emit("notes"))
        btn_today.clicked.connect(lambda: self.page_changed.emit("today"))
        btn_future.clicked.connect(lambda: self.page_changed.emit("future"))
        btn_tasks.clicked.connect(lambda: self.page_changed.emit("tasks"))

        layout.addWidget(btn_today)
        layout.addWidget(btn_notes)
        layout.addWidget(btn_future)
        layout.addWidget(btn_tasks)
        
        layout.addStretch()
        layout.addWidget(QPushButton("Setting"))

        self.setLayout(layout)

