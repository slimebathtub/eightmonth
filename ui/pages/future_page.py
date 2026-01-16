from datetime import date
from PySide6.QtWidgets import (
    QStackedWidget, QHBoxLayout, QWidget,QLabel,
    QVBoxLayout, QPushButton)
from PySide6.QtCore import Signal
from typing import Dict, List

from data.task_repo import TaskRepository
from ui.pages.future_month_view import FutureMonthView
from ui.pages.future_week_view import FutureWeekView

class FutureItem:
    date_str: str          # "YYYY-MM-DD"
    task_id: str
    task_title: str
    milestone_id: int
    milestone_title: str


class FuturePage(QWidget):

    open_task_request = Signal(int)  # task_id

    def __init__(self):
        super().__init__()
        self.repo = TaskRepository()

        self._index: Dict[str, list[FutureItem]] = {}

        self.ui()
        self.now_status = "week"

    
    def ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Top bar
        top = QHBoxLayout()
        title = QLabel("Future")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        top.addWidget(title)

        top.addStretch(1)

        self.btn_week = QPushButton("Week")
        self.btn_month = QPushButton("Month")
        self.btn_week.setCheckable(True)
        self.btn_month.setCheckable(True)

        # default
        self.btn_month.setChecked(True)

        self.btn_week.clicked.connect(lambda: self._set_mode("week"))
        self.btn_month.clicked.connect(lambda: self._set_mode("month"))

        top.addWidget(self.btn_week)
        top.addWidget(self.btn_month)

        root.addLayout(top)

        # stacked views
        self.stack = QStackedWidget()
        self.month_view = FutureMonthView()
        self.week_view = FutureWeekView()

        self.month_view.open_task_requested.connect(self.open_task_request.emit)
        self.week_view.open_task_requested.connect(self.open_task_request.emit)

        self.stack.addWidget(self.month_view)  # index 0
        self.stack.addWidget(self.week_view)   # index 1
        root.addWidget(self.stack, 1)

        self._set_mode("month")
    
    def _set_mode(self, mode: str):
        mode = mode.lower().strip()
        if mode == "week":
            self.btn_week.setChecked(True)
            self.btn_month.setChecked(False)
            self.stack.setCurrentIndex(1)
        else:
            self.btn_week.setChecked(False)
            self.btn_month.setChecked(True)
            self.stack.setCurrentIndex(0)
    
    def reload_index(self):
        """
        Build date->items index from repository.
        Uses milestone.due_date (YYYY-MM-DD). If invalid/missing, skip.
        """
        print("[FuturePage] index days =", len(self._index))
        idx: Dict[str, List[FutureItem]] = {}

        tasks = self.repo.list_tasks_with_milestones()
        for t in tasks:
            task_id = getattr(t, "id", None)
            task_title = getattr(t, "title", "")
            if not task_id:
                continue

            milestones = getattr(t, "milestones", []) or []
            for m in milestones:
                due = getattr(m, "due_date", None)
                mid = getattr(m, "id", None)
                mtitle = getattr(m, "title", "")

                if not due or mid is None:
                    continue

                # validate ISO date
                try:
                    _ = date.fromisoformat(str(due))
                except Exception:
                    continue

                item = FutureItem(
                    date_str=str(due),
                    task_id=str(task_id),
                    task_title=str(task_title),
                    milestone_id=int(mid),
                    milestone_title=str(mtitle),
                )
                idx.setdefault(item.date_str, []).append(item)

        # stable ordering inside a day
        for d in idx:
            idx[d].sort(key=lambda x: (x.task_title.lower(), x.milestone_title.lower()))

        self._index = idx

        # push to views
        self.month_view.set_index(self._index)
        self.week_view.set_index(self._index)
    
    def refresh(self):
        """Optional external call if other pages changed data."""
        self.reload_index()
