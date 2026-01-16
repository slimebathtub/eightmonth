from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout


class DayCard(QWidget):
    """
    A vertical card for a day in Week view.
    items: list objects with attributes:
      - task_id, task_title, milestone_id, milestone_title
    """
    open_task_requested = Signal(str, int)

    def __init__(self, title: str, date_str: str, items: List[object] | None = None, parent=None):
        super().__init__(parent)
        self._title = title
        self._date_str = date_str
        self._items: List[object] = items or []

        self._build_ui()
        self.set_items(self._items)

    def _build_ui(self):
        self.setMinimumWidth(240)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        hdr = QVBoxLayout()
        self.lbl_title = QLabel(self._title)
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: 700;")
        self.lbl_date = QLabel(self._date_str)
        self.lbl_date.setStyleSheet("font-size: 12px; opacity: 0.8;")
        hdr.addWidget(self.lbl_title)
        hdr.addWidget(self.lbl_date)
        root.addLayout(hdr)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        root.addWidget(line)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(8)
        root.addWidget(self.body, 1)

        root.addStretch(1)

        # minimal look (you said you’ll redo later)
        self.setStyleSheet("border: 1px solid rgba(255,255,255,0.2); border-radius: 10px;")

    def set_items(self, items: List[object]):
        self._items = items or []

        # clear
        for i in reversed(range(self.body_layout.count())):
            it = self.body_layout.takeAt(i)
            w = it.widget()
            if w:
                w.deleteLater()

        if not self._items:
            empty = QLabel("—")
            empty.setStyleSheet("opacity: 0.7;")
            self.body_layout.addWidget(empty)
            return

        for it in self._items:
            milestone_title = getattr(it, "milestone_title", "")
            task_title = getattr(it, "task_title", "")
            task_id = getattr(it, "task_id", "")
            mid = int(getattr(it, "milestone_id", 0))

            btn = QPushButton(f"{milestone_title}\n[{task_title}]")
            btn.setStyleSheet("text-align: left; padding: 8px;")
            btn.setMinimumHeight(48)

            def _go(_, tid=task_id, mmid=mid):
                self.open_task_requested.emit(str(tid), int(mmid))

            btn.clicked.connect(_go)
            self.body_layout.addWidget(btn)

        self.body_layout.addStretch(1)
