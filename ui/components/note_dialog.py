from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QMessageBox
)

DELETE_CODE = 99


class NoteDialog(QDialog):
    """
    - New note: note_id=None  -> shows Save/Cancel
    - Edit note: note_id=int  -> shows Save/Cancel/Delete
    """
    def __init__(self, parent=None, title: str = "", content: str = "", note_id: int | None = None):
        super().__init__(parent)
        self.note_id = note_id
        self._result: tuple[str, str] | None = None

        self.setModal(True)
        self.setMinimumWidth(520)
        self.setWindowTitle("New Note" if note_id is None else "Edit Note")

        self.ui()

        self.ed_title.setText(title or "")
        self.ed_content.setPlainText(content or "")

    def ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(10)

        self.ed_title = QLineEdit()
        self.ed_title.setPlaceholderText("Title")

        self.ed_content = QTextEdit()
        self.ed_content.setPlaceholderText("Write something...")

        form.addRow("Title", self.ed_title)
        form.addRow("Content", self.ed_content)

        root.addLayout(form)

        # buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setVisible(self.note_id is not None)
        self.btn_delete.clicked.connect(self._on_delete)

        btn_row.addWidget(self.btn_delete)
        btn_row.addStretch(1)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Save")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self._on_save)

        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)

        root.addLayout(btn_row)

        # optional: style to match your dark glass UI
        self.setStyleSheet("""
            QDialog {
                background: #111;
                color: white;
            }
            QLineEdit, QTextEdit {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 10px;
                padding: 8px;
                selection-background-color: rgba(255,255,255,0.25);
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid rgba(255,255,255,0.25);
            }
            QPushButton {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 10px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.12);
                border: 1px solid rgba(255,255,255,0.18);
            }
        """)

    def _on_save(self):
        title = (self.ed_title.text() or "").strip()
        content = (self.ed_content.toPlainText() or "").strip()

        # 你想允許空 content 也行；但通常 note 內容至少要有字
        if not content:
            QMessageBox.warning(self, "Validation", "Content cannot be empty.")
            return

        # title 可以空，UI 會顯示 (No title)
        self._result = (title, content)
        self.accept()

    def _on_delete(self):
        if QMessageBox.question(self, "Delete", "Delete this note?") == QMessageBox.Yes:
            self.done(DELETE_CODE)

    def result_note(self) -> tuple[str, str] | None:
        """Return (title, content) after Accept."""
        return self._result
