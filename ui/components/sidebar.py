from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtWidgets import QSizePolicy

class SideBar(QWidget):
    page_changed = Signal(str)

    def __init__(self):
        super().__init__()
        print("Sidebar size:", self.width(), self.height())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setObjectName("SideBar")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 30, 0, 20)  


        btn_today = QPushButton("Today")
        btn_notes = QPushButton("Notes")
        btn_future = QPushButton("Future")
        btn_tasks = QPushButton("Tasks")

        for btn in [btn_today, btn_notes, btn_tasks, btn_future]:
            btn.setCheckable(True)

        btn_today.setChecked(True)

        group = QButtonGroup(self)
        group.setExclusive(True)

        for btn in [btn_today, btn_notes, btn_tasks, btn_future]:
            group.addButton(btn)

        btn_notes.clicked.connect(lambda: self.page_changed.emit("notes"))
        btn_today.clicked.connect(lambda: self.page_changed.emit("today"))
        btn_future.clicked.connect(lambda: self.page_changed.emit("future"))
        btn_tasks.clicked.connect(lambda: self.page_changed.emit("tasks"))

        layout.addWidget(btn_today)
        layout.addWidget(btn_notes)
        layout.addWidget(btn_future)
        layout.addWidget(btn_tasks)

        layout.addStretch(1)
        layout.addWidget(QPushButton("Setting"))

        self.setLayout(layout)
    


