from PySide6.QtWidgets import (
    QScrollArea, QPushButton, QWidget, QLabel,
    QHBoxLayout, QVBoxLayout, QGridLayout, QDialog
)
from PySide6.QtCore import Qt
from data.note_repo import NoteRepository
from core.module.note import Note
from ui.components.notecard import NoteCard
from ui.components.note_dialog import NoteDialog, DELETE_CODE


class NotesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = NoteRepository()

        self._cols = 3
        self._notes: list[Note] = []
        self._cards: list[NoteCard] = []
        self._selected_note_id: int | None = None

        self.ui()
        self.reload_notes()

    def ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel("Notes")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        header_row.addWidget(title)
        header_row.addStretch(1)

        self.btn_add = QPushButton("+ Note")
        self.btn_add.setFixedHeight(32)
        self.btn_add.clicked.connect(self._on_add_clicked)
        header_row.addWidget(self.btn_add)
        root.addLayout(header_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)

        self.scroll.setWidget(self.grid_host)
        root.addWidget(self.scroll, 1)

    def reload_notes(self):
        self._notes = self.repo.list_notes()
        self._selected_note_id = None
        self._rebuild_grid()

    def _rebuild_grid(self):
        while self.grid.count():
            it = self.grid.takeAt(0)
            w = it.widget()
            if w:
                w.deleteLater()

        self._cards.clear()

        cols = self._calc_cols()
        self._cols = cols

        card_w = 300
        spacing = self.grid.horizontalSpacing()
        left, top, right, bottom = self.grid.getContentsMargins()
        
        content_w = left + right + cols * card_w + max(0, cols - 1) * spacing
        self.grid_host.setFixedWidth(content_w)


        for i, note in enumerate(self._notes):
            card = NoteCard(note)
            card.clicked.connect(self._on_card_clicked)
            card.double_clicked.connect(self._on_card_double_clicked)

            r = i // cols
            c = i % cols
            self.grid.addWidget(card, r, c)
            self._cards.append(card)

            self.grid.setRowStretch((len(self._notes) // cols) + 1, 1)

    def _calc_cols(self) -> int:
        w = self.scroll.viewport().width()
        card_w = 260
        spacing = 12
        cols = max(1, (w + spacing) // (card_w + spacing))
        return int(min(cols, 3))

    def resizeEvent(self, event):
        new_cols = self._calc_cols()
        if new_cols != self._cols:
            self._cols = new_cols
            self._rebuild_grid()
        super().resizeEvent(event)

    def _on_card_clicked(self, note: Note):
        if note.id is None:
            return
        self._selected_note_id = int(note.id)
        for c in self._cards:
            c.set_selected(int(c.note.id) == self._selected_note_id)

    def _on_add_clicked(self):
        dlg = NoteDialog(self)
        rc = dlg.exec()
        if rc != QDialog.Accepted:
            return
        res = dlg.result_note()
        if not res:
            return
        title, content = res
        self.repo.create_note(title, content)
        self.reload_notes()

    def _on_card_double_clicked(self, note: Note):
        if note.id is None:
            return

        dlg = NoteDialog(self, title=note.title, content=note.content, note_id=int(note.id))
        rc = dlg.exec()

        if rc == DELETE_CODE:
            self.repo.delete_note(int(note.id))
            self.reload_notes()
            return

        if rc != QDialog.Accepted:
            return

        res = dlg.result_note()
        if not res:
            return
        title, content = res
        self.repo.update_note(int(note.id), title=title, content=content)
        self.reload_notes()
