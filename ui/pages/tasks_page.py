from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from ui.components.taskcard import TaskCard


class TasksPage(QWidget):
    def __init__(self):
        super().__init__()
        self._tasks = [
            {"title": "Build To-Do App", "priority": 2, "progress": 68},
            
            {"title": "Buy Groceries", "priority": 4, "progress": 20},
            {"title": "Study for Exams", "priority": 1, "progress": 25},
            {"title": "Email Professor", "priority": 3, "progress": 100},
        ]
        self.ui()

    
    def ui(self):
        # left - right layout
        list_detail_layout = QHBoxLayout(self)
        list_detail_layout.setContentsMargins(16, 16, 16, 16)
        list_detail_layout.setSpacing(14)



        


        # ---- Left: List Side ----
        list_side = QWidget()

        list_side_layout = QVBoxLayout(list_side)
        list_side_layout.setContentsMargins(12, 12, 12, 12)
        list_side_layout.setSpacing(10)


        # ----- Left: Header Row ----
        header_row = QHBoxLayout()
        title = QLabel("Tasks")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        header_row.addWidget(title)

        btn_add = QPushButton("+ Task")
        btn_add.setFixedHeight(32)
        btn_add.clicked.connect(self._on_add_task)
        header_row.addWidget(btn_add)

        list_side_layout.addLayout(header_row)


        for t in self._tasks:
            card = TaskCard(t)
            card.clicked.connect(self._show_detail)
            list_side_layout.addWidget(card)
        
        list_side_layout.addStretch(1)
        

        # ----- Right Tasks detail ---
        detail = QWidget()
        detail.setStyleSheet("background-color: rgb(100,100,200)")
        detail_layout = QVBoxLayout(detail)
        
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(8)

        self.detail_meta = QLabel("—")
        self.detail_title = QLabel("Select a task")
        self.detail_title.setStyleSheet("font-size: 20px; font-weight: 700;")

        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.detail_meta)

        detail_layout.addSpacing(12)


        # --- add to root ---
        list_detail_layout.addWidget(list_side)
        list_detail_layout.addWidget(detail)

        list_detail_layout.setStretch(0, 6)
        list_detail_layout.setStretch(1, 4)
        self.setLayout(list_detail_layout)

        self.setStyleSheet("background-color: rgb(100,200, 100)")

    def _show_detail(self, task: dict):
        self.detail_title.setText(task["title"])
        self.detail_meta.setText(f"Progress: {task['progress']}%   |   Priority: {task['priority']}")
   
    def _on_add_task(self):
        print("Add task clicked")