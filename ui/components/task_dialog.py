from typing import Optional
from dataclasses import replace

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel,
    QFormLayout, QLineEdit, QComboBox, QHBoxLayout, QCheckBox, QDateEdit,
    QSpinBox, QMessageBox, QListWidget, QListWidgetItem
)

from core.module.Task import Task, Milestone
from ui.components.milestone_dialog import MilestoneDialog, DELETE_CODE

class _MilestoneDragList(QListWidget):
    def __init__(self, on_dropped, parent=None):
        super().__init__(parent)
        self._on_dropped = on_dropped

    def dropEvent(self, event):
        super().dropEvent(event)
        # drop 完立即同步順序 + 重新編號
        if callable(self._on_dropped):
            self._on_dropped()

def qdate_to_iso(d: QDate) -> str:
    return d.toString("yyyy-MM-dd")


class TaskDialog(QDialog):
    def __init__(self, parent=None, task: Optional[Task] = None):
        super().__init__(parent)
        self.setWindowTitle("New Task" if task is None else "Edit Task")
        self.setModal(True)

        self._original_task: Optional[Task] = task
        self._result_task: Optional[Task] = None

        # ✅ 小視窗內的暫存 milestones（可拖曳、可編輯、可刪除）
        self._milestones: list[Milestone] = list(task.milestones) if task else []

        self.ui()
        if task is not None:
            self.load_task(task)

        # ✅ load_task 不會動 milestones，所以最後渲染一次
        self._render_milestones()

    def ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.ed_title = QLineEdit()
        self.ed_title.setPlaceholderText("Task title")
        form.addRow("Title", self.ed_title)

        start_row = QHBoxLayout()
        self.cb_use_start = QCheckBox("Use")
        self.de_start = QDateEdit()
        self.de_start.setCalendarPopup(True)
        self.de_start.setDisplayFormat("yyyy-MM-dd")
        self.de_start.setEnabled(False)
        self.cb_use_start.toggled.connect(self.de_start.setEnabled)
        start_row.addWidget(self.cb_use_start)
        start_row.addWidget(self.de_start, 1)
        form.addRow("Start date", start_row)

        due_row = QHBoxLayout()
        self.cb_use_due = QCheckBox("Use")
        self.de_due = QDateEdit()
        self.de_due.setCalendarPopup(True)
        self.de_due.setDisplayFormat("yyyy-MM-dd")
        self.de_due.setEnabled(False)
        self.cb_use_due.toggled.connect(self.de_due.setEnabled)
        due_row.addWidget(self.cb_use_due)
        due_row.addWidget(self.de_due, 1)
        form.addRow("Due date", due_row)

        self.cmb_priority = QComboBox()
        self.cmb_priority.addItem("Emergency", 1)
        self.cmb_priority.addItem("Important", 2)
        self.cmb_priority.addItem("Noticeable", 3)
        self.cmb_priority.addItem("Normal", 4)
        self.cmb_priority.addItem("Relax", 5)
        form.addRow("Priority", self.cmb_priority)

        progress_row = QHBoxLayout()
        self.cmb_progress_mode = QComboBox()
        self.cmb_progress_mode.addItem("Auto", "auto")
        self.cmb_progress_mode.addItem("Manual", "manual")

        self.sp_manual = QSpinBox()
        self.sp_manual.setRange(0, 100)
        self.sp_manual.setSuffix("%")
        self.sp_manual.setEnabled(False)

        self.cmb_progress_mode.currentIndexChanged.connect(self._on_progress_mode_changed)

        progress_row.addWidget(self.cmb_progress_mode, 1)
        progress_row.addWidget(QLabel("Manual:"), 0)
        progress_row.addWidget(self.sp_manual, 0)
        form.addRow("Progress", progress_row)

        root.addLayout(form)

        # ---- Milestones area (in dialog) ----
        root.addWidget(QLabel("Milestones"))

        self.ms_list = _MilestoneDragList(self._after_ms_dropped)
        self.ms_list.setDragDropMode(QListWidget.InternalMove)
        self.ms_list.setDefaultDropAction(Qt.MoveAction)
        self.ms_list.setSelectionMode(QListWidget.SingleSelection)
        root.addWidget(self.ms_list)

        btn_add_ms = QPushButton("+ Milestone")
        btn_add_ms.clicked.connect(self.on_add_milestone)
        root.addWidget(btn_add_ms)

        self.ms_list.itemDoubleClicked.connect(self.on_edit_milestone)


        # ---- buttons ----
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_save = QPushButton("Save")
        self.btn_save.setDefault(True)
        
        if self._original_task is None:
            self.btn_cancel.clicked.connect(self.reject)
        else:
            self.btn_cancel.setText("Delete")
            self.btn_cancel.clicked.connect(self.on_delete_task)

        self.btn_save.clicked.connect(self.on_save)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

        today = QDate.currentDate()
        self.de_start.setDate(today)
        self.de_due.setDate(today)

    def _after_ms_dropped(self):
        self._sync_sort_order_from_ui()
        self._renumber_items()

    
    def _on_progress_mode_changed(self):
        mode = self.cmb_progress_mode.currentData()
        self.sp_manual.setEnabled(mode == "manual")

    def load_task(self, task: Task):
        self.ed_title.setText(task.title)

        idx = self.cmb_priority.findData(task.priority)
        if idx >= 0:
            self.cmb_priority.setCurrentIndex(idx)

        start = getattr(task, "start_date", None)
        due = getattr(task, "due_date", None)

        if start:
            self.cb_use_start.setChecked(True)
            self.de_start.setEnabled(True)
            self.de_start.setDate(QDate.fromString(start, "yyyy-MM-dd"))
        else:
            self.cb_use_start.setChecked(False)
            self.de_start.setEnabled(False)

        if due:
            self.cb_use_due.setChecked(True)
            self.de_due.setEnabled(True)
            self.de_due.setDate(QDate.fromString(due, "yyyy-MM-dd"))
        else:
            self.cb_use_due.setChecked(False)
            self.de_due.setEnabled(False)

        mode = getattr(task, "progress_mode", "auto")
        idx2 = self.cmb_progress_mode.findData(mode)
        if idx2 >= 0:
            self.cmb_progress_mode.setCurrentIndex(idx2)

        manual = getattr(task, "progress_manual", 0) or 0
        self.sp_manual.setValue(int(manual))
        self._on_progress_mode_changed()

    def validate(self) -> bool:
        title = self.ed_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation", "Task title cannot be empty.")
            return False

        if self.cb_use_start.isChecked() and self.cb_use_due.isChecked():
            if self.de_start.date() > self.de_due.date():
                QMessageBox.warning(self, "Validation", "Start date cannot be later than due date.")
                return False
        return True

    # ---------- milestones ----------
    def _render_milestones(self):
        self.ms_list.clear()
        for i, m in enumerate(self._milestones, start=1):
            it = QListWidgetItem(f"{i}. {m.title}")
            it.setFlags(it.flags() | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            it.setData(Qt.UserRole, m)
            self.ms_list.addItem(it)


    def _sync_sort_order_from_ui(self):
        new_list: list[Milestone] = []
        for i in range(self.ms_list.count()):
            it = self.ms_list.item(i)
            m: Milestone = it.data(Qt.UserRole)
            m.sort_order = i
            new_list.append(m)
        self._milestones = new_list

    def on_add_milestone(self):
        dlg = MilestoneDialog(self, None)
        rc = dlg.exec()
        if rc != QDialog.Accepted:
            return

        m = dlg.result()
        if not m:
            return

        self._milestones.append(m)
        self._render_milestones()
        self._sync_sort_order_from_ui()

    def on_edit_milestone(self, item: QListWidgetItem):
        m: Milestone = item.data(Qt.UserRole)

        dlg = MilestoneDialog(self, m)
        rc = dlg.exec()

        if rc == DELETE_CODE:
            self._milestones = [x for x in self._milestones if x is not m]
            self._render_milestones()
            self._sync_sort_order_from_ui()
            return

        if rc != QDialog.Accepted:
            return

        edited = dlg.result()
        if not edited:
            return

        m.title = edited.title
        m.description = edited.description
        m.due_date = edited.due_date
        self._renumber_items()

    def _renumber_items(self):
        # 只改文字，不動 item / model（避免觸發更多內部事件）
        for i in range(self.ms_list.count()):
            it = self.ms_list.item(i)
            m: Milestone = it.data(Qt.UserRole)
            it.setText(f"{i+1}. {m.title}")

    def _on_ms_rows_moved(self, *args):
        self._sync_sort_order_from_ui()
        self._renumber_items()

    # ---------- save ----------
    def on_save(self):
        if not self.validate():
            return

        # ✅ 保證用拖曳後的新順序
        self._sync_sort_order_from_ui()

        title = self.ed_title.text().strip()
        priority = int(self.cmb_priority.currentData())

        start_date = qdate_to_iso(self.de_start.date()) if self.cb_use_start.isChecked() else None
        due_date = qdate_to_iso(self.de_due.date()) if self.cb_use_due.isChecked() else None

        progress_mode = self.cmb_progress_mode.currentData()
        progress_manual = int(self.sp_manual.value()) if progress_mode == "manual" else 0

        if self._original_task is None:
            self._result_task = Task(
                title=title,
                priority=priority,
                progress_mode=progress_mode,
                progress_manual=progress_manual,
                start_date=start_date,
                due_date=due_date,
                milestones=list(self._milestones),
            )
        else:
            t = self._original_task
            self._result_task = replace(
                t,
                title=title,
                priority=priority,
                progress_mode=progress_mode,
                progress_manual=progress_manual,
                start_date=start_date,
                due_date=due_date,
            )
            self._result_task.milestones = list(self._milestones)

        self.accept()

    def result_task(self) -> Optional[Task]:
        return self._result_task
    
    def on_delete_task(self):
        if QMessageBox.question(self, "Delete", "Delete this task?") == QMessageBox.Yes:
            self.done(DELETE_CODE)


