from PySide6.QtWidgets import (
    QScrollArea, QWidget, QHBoxLayout, QLabel, QVBoxLayout,
    QPushButton, QCheckBox, QInputDialog, QDialog, QToolButton
)
from PySide6.QtCore import Qt
from ui.components.taskcard import TaskCard
from core.module.Task import Task
from data.task_repo import TaskRepository
from ui.components.task_dialog import TaskDialog

from ui.components.milestone_list import MilestoneListWidget
from ui.components.milestone_dialog import MilestoneDialog, DELETE_CODE
from core.module.Task import Milestone
from PySide6.QtCore import QSignalBlocker, QTimer

import time

class TasksPage(QWidget):
    def __init__(self):
        super().__init__()
        self._sort_mode = "urgency"
        self.repo = TaskRepository()
        self._task_cards: dict[str, TaskCard] = {}
        self._selected_task_id: str | None = None
        self._tasks: list[Task] = []
        self._task_dialog_open = False
        # self._block_card_clicks_until = 0.0

        self.ui()
        self.reload_tasks()

    def ui(self):
        # root layout
        self.list_detail_layout = QHBoxLayout(self)
        self.list_detail_layout.setContentsMargins(16, 16, 16, 16)
        self.list_detail_layout.setSpacing(14)

        # ---- Left: List Side ----
        list_side = QWidget()
        self.list_side_layout = QVBoxLayout(list_side)
        self.list_side_layout.setContentsMargins(12, 12, 12, 12)
        self.list_side_layout.setSpacing(10)

        # Header Row
        header_row = QHBoxLayout()
        title = QLabel("Tasks")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        header_row.addWidget(title)

        # ---- sort switch (新增) ----
        self.sort_btn = QToolButton()
        self.sort_btn.setCheckable(True)
        self.sort_btn.setChecked(False)  # False=urgency
        self._update_sort_btn_text()
        self.sort_btn.clicked.connect(self._on_sort_btn_clicked)

        header_row.addWidget(self.sort_btn)


        btn_add = QPushButton("+ Task")
        btn_add.setFixedHeight(32)
        btn_add.clicked.connect(self._on_add_task)
        header_row.addWidget(btn_add)

        self.list_side_layout.addLayout(header_row)

        # ------ Cards container (rendered by reload_tasks)-----
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)

        # ------- Scroll Area for cards -----
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setWidget(self.cards_container)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.list_side_layout.addWidget(self.scroll)

        # ---- Right: Task detail ----
        detail = QWidget()
        detail.setStyleSheet("background-color: rgb(100,100,200)")
        detail_layout = QVBoxLayout(detail)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(8)

        self.detail_title = QLabel("Select a task")
        self.detail_title.setStyleSheet("font-size: 20px; font-weight: 700;")
        self.date_info = QLabel("")
        self.detail_meta = QLabel("")

        self.milestone_list = QWidget()
        self.milestone_list_layout = QVBoxLayout(self.milestone_list)
        self.milestone_list_layout.setContentsMargins(0, 0, 0, 0)
        self.milestone_list_layout.setSpacing(6)

        # add to root
        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.date_info)
        detail_layout.addWidget(self.detail_meta)
        detail_layout.addWidget(self.milestone_list)

        self.list_detail_layout.addWidget(list_side)
        self.list_detail_layout.addWidget(detail)

        self.list_detail_layout.setStretch(0, 6)
        self.list_detail_layout.setStretch(1, 4)

        self.setStyleSheet("background-color: rgb(100,200, 100)")

    def _select_and_focus_task(self, task_id: str, scroll_into_view: bool = True):
        self._selected_task_id = task_id

        # 1) 更新每張卡的 selected 外觀
        for tid, card in self._task_cards.items():
            card.set_selected(tid == task_id)

        # 2) 右側 detail 顯示該 task（用最新資料）
        latest = self.repo.get_task(task_id)
        if latest:
            self._show_detail(latest)

        # 3) 左側捲到該卡（等 layout 穩定後再捲）
        if scroll_into_view and task_id in self._task_cards:
            card = self._task_cards[task_id]
            QTimer.singleShot(0, lambda: self.scroll.ensureWidgetVisible(card))
    
    def _update_sort_btn_text(self):
        self.sort_btn.setText("A→Z" if self.sort_btn.isChecked() else "Urgency")

    def _on_sort_btn_clicked(self):
        self._sort_mode = "alpha" if self.sort_btn.isChecked() else "urgency"
        self._update_sort_btn_text()
        self.reload_tasks(keep_scroll=True, keep_selection=True)


    def reload_tasks(self, keep_scroll: bool = True, keep_selection: bool = True):
        

        # ---- preserve scroll position ----
        sb = self.scroll.verticalScrollBar()
        old_scroll = sb.value() if keep_scroll else 0

        # ---- preserve selection ----
        selected_id = self._selected_task_id if keep_selection else None

        # 0) rebuild 期間擋一下 click（避免你之前那種閃窗連發）
        # self._block_card_clicks_until = time.time() + 0.35

        # 1) clear cards
        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.takeAt(i)
            w = item.widget()
            if w:
                w.setEnabled(False)
                w.setParent(None)
                w.deleteLater()

        self._task_cards.clear()

        # 2) load tasks
        self._tasks = self.repo.list_tasks_with_milestones()

        # 2.5) sort tasks
        tasks = list(self._tasks)
        if self._sort_mode == "alpha":
            tasks.sort(key=lambda t: (t.title or "").strip().lower())
        else:
            # urgency: priority 越小越緊急
            tasks.sort(key=lambda t: (getattr(t, "priority", 999), (t.title or "").strip().lower()))

        # 3) rebuild cards
        for t in tasks:
            card = TaskCard(t)

            card.clicked.connect(self._show_detail, Qt.UniqueConnection)
            card.double_clicked.connect(self._on_edit_task, Qt.UniqueConnection)

            card.set_selected(t.id == selected_id)
            self.cards_layout.addWidget(card)
            self._task_cards[t.id] = card

        self.cards_layout.addStretch(1)

        # 4) restore selection + detail
        self._selected_task_id = selected_id
        if selected_id:
            latest = self.repo.get_task(selected_id)
            if latest:
                blocker = QSignalBlocker(self)
                self._show_detail(latest)
                del blocker

        # 5) restore scroll (重建後下一個 event loop 再設，才不會被 layout 立刻改回去)
        if keep_scroll:
            QTimer.singleShot(0, lambda: sb.setValue(old_scroll))


    def _show_detail(self, task: Task):
        
        self._selected_task_id = task.id
        for tid, card in self._task_cards.items():
            card.set_selected(tid == self._selected_task_id)

        task = self.repo.get_task(task.id) or task

        # title / date / meta
        self.detail_title.setText(task.title)

        start_date = getattr(task, "start_date", "")
        due_date = getattr(task, "due_date", "")
        if start_date or due_date:
            self.date_info.setText(f"Start: {start_date}   -   End: {due_date}")
        else:
            self.date_info.setText("")

        self.detail_meta.setText(f"Progress: {task.progress}%   |   Priority: {task.priority}")

        # milestones list
        self._clear_milestones_ui()

        for m in task.milestones:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            # ---- Left block (title + description) ----
            left = QWidget()
            left_layout = QVBoxLayout(left)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setSpacing(2)

            cb = QCheckBox(m.title)
            cb.blockSignals(True)
            cb.setChecked(bool(m.done))
            cb.blockSignals(False)

            desc = (m.description or "").strip()
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: rgba(255,255,255,0.65); font-size: 12px;")
            desc_label.setVisible(bool(desc))   # ✅ 沒描述就不顯示

            left_layout.addWidget(cb)
            left_layout.addWidget(desc_label)

            # ---- Right block (due) ----
            m_due = getattr(m, "due_date", None)
            due_text = f"Due: {m_due}" if m_due else "Due: —"
            due_label = QLabel(due_text)
            due_label.setStyleSheet("color: rgba(255,255,255,0.65); font-size: 12px;")

            def on_toggle(checked, mid=m.id, tid=task.id):
                self.repo.set_milestone_done(mid, checked)
                latest = self.repo.get_task(tid)
                if latest:
                    self.detail_meta.setText(f"Progress: {latest.progress}%   |   Priority: {latest.priority}")
                    card = self._task_cards.get(tid)
                    if card:
                        card.task = latest
                        card.update_view()

            cb.toggled.connect(on_toggle)

            row_layout.addWidget(left, 1)
            row_layout.addStretch(1)
            row_layout.addWidget(due_label)

            self.milestone_list_layout.addWidget(row)




    def _on_add_task(self):
        dlg = TaskDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return

        t = dlg.result_task()
        if not t:
            return

        created_id = self.repo.create_task(t)  # 如果 repo 沒回傳，就會是 None
        
        task_id = created_id or getattr(t, "id", None)
        for m in t.milestones:
            self.repo.add_milestone(task_id, m)

        # auto choose
        self._selected_task_id = task_id
        self.reload_tasks()

        # show up in the right
        if task_id:
            latest = self.repo.get_task(task_id)
            if latest:
                self._show_detail(latest)

    def _clear_milestones_ui(self):
        for i in reversed(range(self.milestone_list_layout.count())):
            item = self.milestone_list_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()

    def _on_edit_task(self, task: Task):
        # if time.time() < self._block_card_clicks_until:
        #    return
        sender = self.sender()
        if self._task_dialog_open:
            return
        self._task_dialog_open = True
        try:
            latest = self.repo.get_task(task.id) or task

            dlg = TaskDialog(self, latest)
            rc = dlg.exec()

            if rc == DELETE_CODE:
                self.repo.delete_task(latest.id)
                self._selected_task_id = None
                self.reload_tasks()
                self.detail_title.setText("Select a task")
                self.date_info.setText("")
                self.detail_meta.setText("")
                self._clear_milestones_ui()
                return

            if rc != QDialog.Accepted:
                return

            updated = dlg.result_task()
            if not updated:
                return

            self.repo.update_task(updated)
            self._sync_milestones(updated)

            edited_id = task.id
            self._selected_task_id = edited_id
            self.reload_tasks(keep_scroll=True, keep_selection=True)
            self._select_and_focus_task(edited_id, scroll_into_view=True)
        finally:
            self._task_dialog_open = False
            # self._block_card_clicks_until = time.time() + 0.25



    def _sync_milestones(self, task: Task):
        existing = self.repo.get_task(task.id)
        existing_by_id = {m.id: m for m in (existing.milestones if existing else []) if m.id is not None}

        new_ids = set()

        for idx, m in enumerate(task.milestones):
            m.sort_order = idx

            if m.id is None:
                new_id = self.repo.add_milestone(task.id, m)
                m.id = new_id
                new_ids.add(new_id)
            else:
                new_ids.add(m.id)
                self.repo.update_milestone(
                    int(m.id),
                    title=m.title,
                    description=m.description,
                    due_date=m.due_date,
                    sort_order=m.sort_order,
                    done=m.done,
                )

        # delete removed
        for mid in existing_by_id.keys():
            if mid not in new_ids:
                self.repo.delete_milestone(int(mid))



