from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QFrame
)
from PySide6.QtCore import QDate
from data.task_repo import TaskRepository
from ui.components.relax import RelaxListWidget


class TodayMilestoneRow(QFrame):
    def __init__(self, milestone_title: str, task_title: str, due_text: str):
        super().__init__()
        self.setObjectName("TodayMilestoneRow")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(2)

        title = QLabel(milestone_title)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")

        sub = QLabel(f"from: {task_title}")
        sub.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.65);")

        due = QLabel(f"due: {due_text}")
        due.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.65);")

        root.addWidget(title)
        root.addWidget(sub)
        root.addWidget(due)

        self.setStyleSheet("""
            QFrame#TodayMilestoneRow {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
            }
        """)


class TodayPage(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = TaskRepository()
        self.ui()
        self.reload_today()

    def _clear_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _format_due_text(self, m) -> str:
        due_date = getattr(m, "due_date", None)
        if not due_date:
            return "No due date"

        d = QDate.fromString(due_date, "yyyy-MM-dd")
        if d.isValid():
            return d.toString("MMM d")  # Jan 13
        return str(due_date)

    def _is_due_today(self, m) -> bool:
        today_str = QDate.currentDate().toString("yyyy-MM-dd")
        return getattr(m, "due_date", None) == today_str

    def reload_today(self):
        self._clear_list()

        tasks = self.repo.list_tasks_with_milestones()
        count = 0

        for t in tasks:
            for m in t.milestones:
                if self._is_due_today(m):
                    due_text = self._format_due_text(m)
                    self.list_layout.addWidget(
                        TodayMilestoneRow(m.title, t.title, due_text)
                    )
                    count += 1

        if count == 0:
            empty = QLabel("No milestones due today!")
            empty.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.5);")
            self.list_layout.addWidget(empty)

        self.list_layout.addStretch(1)

        if hasattr(self, "relax_widget"):
            self.relax_widget.reload_relax_items()

    def ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        # ---- title row ----
        title_row = QWidget()
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        title = QLabel("Today")
        date = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
        self.task_amount = QLabel("Task amount: 0")

        title_layout.addWidget(title)
        title_layout.addWidget(date)
        title_layout.addStretch(1)
        title_layout.addWidget(self.task_amount)

        # ---- detail (left/right) ----
        detail = QHBoxLayout()
        detail.setContentsMargins(0, 0, 0, 0)
        detail.setSpacing(10)

        # ---- left ----
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)

        left_title = QLabel("Tasks")
        left_layout.addWidget(left_title)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidget(self.list_container)

        left_layout.addWidget(scroll)

        # ---- right ----
        right = QWidget()
        right_layout = QVBoxLayout(right)

        right_title = QLabel("Routine/Relax")
        self.relax_widget = RelaxListWidget()

        right_layout.addWidget(right_title)
        right_layout.addWidget(self.relax_widget)

        right_layout.setContentsMargins(12, 12, 12, 12)
        right_layout.setSpacing(10)
        right_layout.addStretch(1)

        detail.addWidget(left, 7)
        detail.addWidget(right, 3)

        # ---- assemble ----
        root.addWidget(title_row)
        root.addLayout(detail)
    
