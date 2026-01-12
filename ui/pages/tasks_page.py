from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QCheckBox
from ui.components.taskcard import TaskCard
from core.module.Task import Task
from data.task_repo import TaskRepository


class TasksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = TaskRepository()
        self._task_cards: dict[str, TaskCard] = {}
        self._selected_task_id: str | None = None
        self._tasks: list[Task] = []

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

        btn_add = QPushButton("+ Task")
        btn_add.setFixedHeight(32)
        btn_add.clicked.connect(self._on_add_task)
        header_row.addWidget(btn_add)

        self.list_side_layout.addLayout(header_row)

        # Cards container (rendered by reload_tasks)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)

        self.list_side_layout.addWidget(self.cards_container)
        self.list_side_layout.addStretch(1)

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

        detail_layout.addWidget(self.detail_title)
        detail_layout.addWidget(self.date_info)
        detail_layout.addWidget(self.detail_meta)
        detail_layout.addWidget(self.milestone_list)
        detail_layout.addSpacing(12)

        # add to root
        self.list_detail_layout.addWidget(list_side)
        self.list_detail_layout.addWidget(detail)

        self.list_detail_layout.setStretch(0, 6)
        self.list_detail_layout.setStretch(1, 4)

        self.setStyleSheet("background-color: rgb(100,200, 100)")

    def reload_tasks(self):
        # clear cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self._task_cards.clear()
        self._tasks = self.repo.list_tasks_with_milestones()

        for t in self._tasks:
            card = TaskCard(t)
            card.clicked.connect(self._show_detail)
            self.cards_layout.addWidget(card)
            self._task_cards[t.id] = card

        self.cards_layout.addStretch(1)

        # if a task is selected, refresh its detail with latest data
        if self._selected_task_id:
            latest = self.repo.get_task(self._selected_task_id)
            if latest:
                self._show_detail(latest)

    def _clear_milestones_ui(self):
        for i in reversed(range(self.milestone_list_layout.count())):
            item = self.milestone_list_layout.takeAt(i)
            w = item.widget()
            if w:
                w.deleteLater()

    def _show_detail(self, task: Task):
        self._selected_task_id = task.id
        task = self.repo.get_task(task.id) or task

        # title / date / meta
        self.detail_title.setText(task.title)

        start_date = getattr(task, "start_date", "")
        due_date = getattr(task, "due_date", "")
        if start_date or due_date:
            self.date_info.setText(f"Start: {start_date}   -   End: {due_date}")
        else:
            self.date_info.setText("")

        self.detail_meta.setText(f"Progress: {task.progress()}%   |   Priority: {task.priority}")

        # milestones list
        self._clear_milestones_ui()

        for m in task.milestones:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            cb = QCheckBox(m.title)
            cb.blockSignals(True)
            cb.setChecked(bool(m.done))
            cb.blockSignals(False)

            m_due = getattr(m, "due_date", None)
            due_text = f"Due: {m_due}" if m_due else "Due: —"
            due_label = QLabel(due_text)
            due_label.setStyleSheet("color: rgba(255,255,255,0.65); font-size: 12px;")

            def on_toggle(checked, mid=m.id, tid=task.id):
                # 只更新單一 milestone，不要 replace 全部
                self.repo.set_milestone_done(mid, checked)

                latest = self.repo.get_task(tid)
                if latest:
                    self.detail_meta.setText(
                        f"Progress: {latest.progress()}%   |   Priority: {latest.priority}"
                    )
                    card = self._task_cards.get(tid)
                    if card:
                        card.task = latest
                        card.update_view()

                # 你想保險就整頁重載（穩但會閃一下）
                self.reload_tasks()

            cb.toggled.connect(on_toggle)

            row_layout.addWidget(cb)
            row_layout.addStretch(1)
            row_layout.addWidget(due_label)

            self.milestone_list_layout.addWidget(row)

    def _on_add_task(self):
        print("Add task clicked")
