from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QCheckBox
from ui.components.taskcard import TaskCard
from core.module.Task import Task, Milestone

task1 = Task({
    "title": "Build To-Do App",
    "priority": 2,
    "milestones": [
        Milestone("UI Draft", True, "", "2024-01-05"),
        Milestone("Backend Logic", True, "", "2024-01-10"),
        Milestone("Sidebar", True, "", "2024-01-15"),
        Milestone("Tasks Page", False, "", "2024-01-20"),
        Milestone("Polish", False, "", "2024-01-31"),
    ],
    "start_date": "2024-01-01",
    "due_date": "2024-01-31",
    "progress_mode": "auto",
})

task2 = Task({
    "title": "Write Blog Post",
    "priority": 3,
    "milestones": [
        Milestone("Research", True,"",  "2024-02-03"),
        Milestone("Draft", False,"",  "2024-02-05"),
        Milestone("Edit", False, "", "2024-02-07"),
        Milestone("Publish", False, "", "2024-02-10"),
    ],
    "progress_mode": "manual",
    "start_date": "2024-02-01",
    "due_date": "2024-02-10",
    "progress_manual": 19,
})



class TasksPage(QWidget):
    def __init__(self):
        super().__init__()
        self._tasks = [task1, task2]
        self._task_cards = {}
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
        
            self._task_cards[id(t)] = card
        list_side_layout.addStretch(1)
        

        # ----- Right Tasks detail ---
        detail = QWidget()
        detail.setStyleSheet("background-color: rgb(100,100,200)")
        detail_layout = QVBoxLayout(detail)
        
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(8)
        self.detail_meta = QLabel("")
        self.detail_title = QLabel("Select a task")
        self.date_info = QLabel("")
        self.detail_title.setStyleSheet("font-size: 20px; font-weight: 700;")

        self.milestone_list = QWidget()
        self.milestone_list_layout = QVBoxLayout(self.milestone_list)
        self.milestone_list_layout.setContentsMargins(0, 0, 0, 0)
        self.milestone_list_layout.setSpacing(6)
        

        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.date_info)
        detail_layout.addWidget(self.detail_meta)
        detail_layout.addWidget(self.milestone_list)


        detail_layout.addSpacing(12)


        # --- add to root ---
        list_detail_layout.addWidget(list_side)
        list_detail_layout.addWidget(detail)

        list_detail_layout.setStretch(0, 6)
        list_detail_layout.setStretch(1, 4)
        self.setLayout(list_detail_layout)

        self.setStyleSheet("background-color: rgb(100,200, 100)")

    def _show_detail(self, task: Task):
        # 1) update title / meta info
        self.detail_title.setText(task.title)

        start_date = getattr(task, "start_date", "")
        due_date = getattr(task, "due_date", "")
        if start_date or due_date:
            self.date_info.setText(f"Start: {start_date}   -   End: {due_date}")
        else:
            self.date_info.setText("")

        self.detail_meta.setText(f"Progress: {task.progress()}%   |   Priority: {task.priority}")

        # 2) delete the old milestone UI
        for i in reversed(range(self.milestone_list_layout.count())):
            item = self.milestone_list_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 3) create a new milestone checklist
        for m in task.milestones:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            cb = QCheckBox(m.title)
            cb.setChecked(m.done)

            # 取 milestone 的 due_date（如果 Milestone 還沒有這個屬性，就顯示 —）
            m_due = getattr(m, "due_date", None)
            due_text = f"Due: {m_due}" if m_due else "Due: —"
            due_label = QLabel(due_text)
            due_label.setStyleSheet("color: rgba(255,255,255,0.65); font-size: 12px;")

            # ✅ 勾選時同步更新資料 + 進度文字（不然 UI 不會跟著變）
            def on_toggle(checked, milestone=m, current_task=task):
                milestone.done = checked

                if getattr(current_task, "progress_mode", "auto") == "manual":
                    current_task.progress_mode = "auto"

                self.detail_meta.setText(
                    f"Progress: {current_task.progress()}%   |   Priority: {current_task.priority}"
                )

                card = self._task_cards.get(id(current_task))
                if card:
                    card.update_view()

            cb.toggled.connect(on_toggle)

            row_layout.addWidget(cb)
            row_layout.addStretch(1)
            row_layout.addWidget(due_label)

            self.milestone_list_layout.addWidget(row)


    def _on_add_task(self):
        print("Add task clicked")
