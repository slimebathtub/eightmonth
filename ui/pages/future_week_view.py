from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List
from shiboken6 import isValid


from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame
)

from ui.components.day_card import DayCard


class FutureWeekView(QWidget):
    open_task_requested = Signal(str, int)

    def __init__(self):
        super().__init__()

        self._scroll_timer = QTimer(self)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.timeout.connect(lambda: self.focus_today(center=True))
        
        self._index: Dict[str, List[object]] = {}
        self._week_start: date = date.today()
        self._day_cards = []


        self._build_ui()
        self.set_week_start(date.today())

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        # week nav
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Prev Week")
        self.btn_next = QPushButton("Next Week ▶")
        self.lbl_range = QLabel("")
        self.lbl_range.setStyleSheet("font-size: 14px; font-weight: 600;")

        nav.addWidget(self.btn_prev)
        nav.addWidget(self.lbl_range)
        nav.addStretch(1)
        nav.addWidget(self.btn_next)

        root.addLayout(nav)

        # horizontal scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.hbox = QHBoxLayout(self.container)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(12)

        self.scroll.setWidget(self.container)
        root.addWidget(self.scroll, 1)

        self.btn_prev.clicked.connect(lambda: self.set_week_start(self._week_start - timedelta(days=7)))
        self.btn_next.clicked.connect(lambda: self.set_week_start(self._week_start + timedelta(days=7)))


    # ---------- public ----------
    def set_index(self, index: Dict[str, List[object]]):
        self._index = index or {}
        self._rebuild_cards()

    def set_week_start(self, any_day: date):
        """
        Use 'any_day' as anchor; week is 7 consecutive days starting from that day.
        (You can change to Monday-based if you prefer.)
        """
        self._week_start = any_day
        self._rebuild_cards()

    # ---------- internal ----------
    def _rebuild_cards(self):
        if self._scroll_timer.isActive(): 
            self._scroll_timer.stop()
        # clear cards
        for i in reversed(range(self.hbox.count())):
            it = self.hbox.takeAt(i)
            w = it.widget()
            if w:
                w.deleteLater()

        self._day_cards = []

        start = self._week_start
        end = self._week_start + timedelta(days=6)
        self.lbl_range.setText(f"{start.isoformat()}  →  {end.isoformat()}")

        for i in range(7):
            d = start + timedelta(days=i)
            ds = d.isoformat()
            items = self._index.get(ds, [])

            title = d.strftime("%a")  # Mon/Tue...
            card = DayCard(title=title, date_str=ds, items=items)
            card.open_task_requested.connect(self.open_task_requested.emit)

            self._day_cards.append((d, card))
            self.hbox.addWidget(card)

        self.hbox.addStretch(1)

        # --- auto focus to today (if today is in this week) ---
        self._scroll_to_today_if_visible()
    
    def showEvent(self, event):
        super().showEvent(event)
        # 等 UI 真正 layout 完再捲
        self._scroll_timer.start(0)
    
    def set_week_start(self, any_day: date):
        """
        Always align to Monday.
        any_day can be any date; we normalize it to that week's Monday.
        """
        # Monday = 0, Sunday = 6
        monday = any_day - timedelta(days=any_day.weekday())
        self._week_start = monday
        self._rebuild_cards()
    
    def _scroll_to_today_if_visible(self):
        """Keep this name if you already call it elsewhere."""
        self.focus_today(center=True)

    def focus_today(self, center: bool = True):
        today = date.today()
        if not (self._week_start <= today <= self._week_start + timedelta(days=6)):
            return

        target = None
        if not isValid(target):
            return
        for d, card in self._day_cards:
            if d == today:
                target = card
                break
        if not target:
            return

        def _do_scroll():
            from shiboken6 import isValid
            if not isValid(target): 
                return
            bar = self.scroll.horizontalScrollBar()

            # 如果此時 scrollbar 還沒更新（max=0 或 pos=0），晚一點再試一次
            if bar.maximum() == 0 and self.container.width() <= self.scroll.viewport().width():
                QTimer.singleShot(50, _do_scroll)
                return

            x = target.geometry().x()  # 相對於 container 的 x（比 pos() 更穩）
            if center:
                center_value = x - (self.scroll.viewport().width() - target.width()) // 2
                bar.setValue(max(0, min(bar.maximum(), center_value)))
            else:
                bar.setValue(max(0, min(bar.maximum(), x)))

        # 先等 layout 一下，再捲；0 有時太早，20~50 更穩
        QTimer.singleShot(30, _do_scroll)


