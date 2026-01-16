from PySide6.QtWidgets import (
    QScrollArea, QLabel, QDialog, QVBoxLayout, QFrame,
    QWidget, QPushButton, QHBoxLayout, QCalendarWidget,
)
from PySide6.QtGui import QTextCharFormat, QFont
from PySide6.QtCore import Qt, QDate, Signal
from typing import Dict, List
from datetime import date



class DayItemDialog(QDialog):
    open_task_requested = Signal(str, int)  # task_id

    def __init__(self, date_str: str, items: List[object], parent = None):
        super().__init__()
        self.date_str = date_str
        self.ui(date_str, items)

    def ui(self, date_str: str, items: List[object], parent = None):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QLabel(f"Items on {date_str}")
        header.setStyleSheet("font-size: 16px; font-weight: 700;")
        root.addWidget(header)

        # scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(8)

        for it in items:
            btn = QPushButton(f"{getattr(it, 'milestone_title', '')}\n[{getattr(it, 'task_title', '')}]")
            btn.setMinimumHeight(48)
            btn.setStyleSheet("text-align: left; padding: 8px;")
            task_id = getattr(it, "task_id", "")
            mid = int(getattr(it, "milestone_id", 0))

            def _go(_, tid=task_id, mmid=mid):
                self.open_task_requested.emit(str(tid), int(mmid))
                self.accept()

            btn.clicked.connect(_go)
            body_layout.addWidget(btn)

        body_layout.addStretch(1)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        root.addWidget(close_btn, 0, Qt.AlignRight)
    

class FutureMonthView(QWidget):
    open_task_requested = Signal(str, int)  # task_id

    def __init__(self):
        super().__init__()
        self._index: Dict[str, List[object]] = {}
        self.ui()

    def ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # Month nav row
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.lbl_month = QLabel("")
        self.lbl_month.setStyleSheet("font-size: 14px; font-weight: 600;")
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.lbl_month)
        nav.addWidget(self.btn_next)
        nav.addStretch(1)

        root.addLayout(nav)

        self.cal = QCalendarWidget()
        self.cal.setGridVisible(True)
        root.addWidget(self.cal, 1)

        self.btn_prev.clicked.connect(self._prev_month)
        self.btn_next.clicked.connect(self._next_month)
        self.cal.currentPageChanged.connect(lambda y, m: self._update_month_label())
        self.cal.clicked.connect(self._on_date_clicked)

        self._update_month_label()
    
    def set_index(self, index: Dict[str, list[object]]):
        self._index = index or {}
        self._apply_date_markers()

    # ------ calender -------

    def _update_month_label(self):
        y = self.cal.yearShown()
        m = self.cal.monthShown()
        self.lbl_month.setText(f"{y}-{m:02d}")
        self._apply_date_markers()

    def _prev_month(self):
        self.cal.showPreviousMonth()
        self._update_month_label()

    def _next_month(self):
        self.cal.showNextMonth()
        self._update_month_label()

    def _apply_date_markers(self):
        """
        Mark dates in currently shown month that have items.
        Keep it simple: bold + slightly different text format.
        """
        # reset formats for whole shown month range: just clear the visible month days we know
        y = self.cal.yearShown()
        m = self.cal.monthShown()

        normal = QTextCharFormat()
        normal.setFontWeight(QFont.Normal)

        marked = QTextCharFormat()
        marked.setFontWeight(QFont.Bold)

        # iterate all keys that belong to current shown month
        for ds, items in self._index.items():
            try:
                d = date.fromisoformat(ds)
            except Exception:
                continue
            qd = QDate(d.year, d.month, d.day)
            if d.year == y and d.month == m:
                # mark if there are items
                if items:
                    self.cal.setDateTextFormat(qd, marked)
                else:
                    self.cal.setDateTextFormat(qd, normal)

        # (optional) if you want to clear other dates format in this month,
        # you can loop day 1..31 and set normal, but it's unnecessary for MVP.

    def _on_date_clicked(self, qdate: QDate):
        
        ds = qdate.toString("yyyy-MM-dd")
        items = self._index.get(ds, [])
        
        dlg = DayItemDialog(ds, items, parent=self)
        dlg.open_task_requested.connect(self.open_task_requested.emit)
        dlg.exec()