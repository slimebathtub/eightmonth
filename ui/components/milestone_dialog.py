from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QDateEdit,
    QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import QDate
from core.module.Task import Milestone

DELETE_CODE = 99  # 自訂：代表使用者按了 Delete


class MilestoneDialog(QDialog):
    def __init__(self, parent=None, milestone: Milestone | None = None):
        super().__init__(parent)
        self.setModal(True)

        self._original = milestone
        self._result: Milestone | None = None

        self.setWindowTitle("Add Milestone" if milestone is None else "Edit Milestone")
        self.ui()

        if milestone:
            self.load(milestone)

    def ui(self):
        root = QVBoxLayout(self)
        form = QFormLayout()

        self.ed_title = QLineEdit()
        self.ed_desc = QTextEdit()

        self.de_due = QDateEdit()
        self.de_due.setCalendarPopup(True)
        self.de_due.setDisplayFormat("yyyy-MM-dd")
        self.de_due.setDate(QDate.currentDate())

        form.addRow("Title", self.ed_title)
        form.addRow("Description", self.ed_desc)
        form.addRow("Due date", self.de_due)

        root.addLayout(form)

        btns = QHBoxLayout()

        # Delete（只有編輯時顯示）
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setVisible(self._original is not None and self._original.id is not None)
        self.btn_delete.clicked.connect(self.on_delete)

        btns.addWidget(self.btn_delete)
        btns.addStretch(1)

        btn_cancel = QPushButton("Cancel")
        btn_save = QPushButton("Save")
        btn_save.setDefault(True)

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.on_save)

        btns.addWidget(btn_cancel)
        btns.addWidget(btn_save)

        root.addLayout(btns)

    def load(self, m: Milestone):
        self.ed_title.setText(m.title)
        self.ed_desc.setPlainText(m.description or "")
        if m.due_date:
            self.de_due.setDate(QDate.fromString(m.due_date, "yyyy-MM-dd"))

    def on_save(self):
        title = self.ed_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Validation", "Title required")
            return

        due = self.de_due.date().toString("yyyy-MM-dd")
        self._result = Milestone(
            id=getattr(self._original, "id", None),
            title=title,
            description=self.ed_desc.toPlainText(),
            due_date=due,
            done=getattr(self._original, "done", False),
            sort_order=getattr(self._original, "sort_order", 0),
        )
        self.accept()

    def on_delete(self):
        if QMessageBox.question(self, "Delete", "Delete this milestone?") == QMessageBox.Yes:
            self.done(DELETE_CODE)

    def result(self) -> Milestone | None:
        return self._result
