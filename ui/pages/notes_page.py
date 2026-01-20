from PySide6.QtWidgets import (
    QScrollArea, QPushButton, QWidget, QLabel,
    QHBoxLayout, QVBoxLayout, QGridLayout, QApplication
)
from PySide6.QtCore import Qt

from data.note_repo import NoteRepository
from core.module.note import Note
from ui.components.notecard import NoteCard
from ui.components.note_dialog import NoteDialog

import time
class NotesPage(QWidget):
    CARD_W = 260   # 跟 NoteCard 裡固定寬一致（你 notecard.py 是 300）:contentReference[oaicite:2]{index=2}
    SPACING = 12
    MAX_COLS = 3

    def __init__(self):
        super().__init__()
        print("[NotesPage] created", id(self))
        self.repo = NoteRepository()
        
        self._block_clicks_until = 0.0


        self._cols = 3
        self._notes: list[Note] = []
        self._cards: list[NoteCard] = []
        self._selected_note_id: int | None = None

        # 每個 page 的鎖（保留）
        self._active_note_dlg: NoteDialog | None = None

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
        self.grid.setHorizontalSpacing(self.SPACING)
        self.grid.setVerticalSpacing(self.SPACING)

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
                w.setParent(None)
                w.deleteLater()

        self._cards.clear()

        cols = self._calc_cols()
        self._cols = cols

        # 固定 host 寬度，兩欄置中會好看
        left, top, right, bottom = self.grid.getContentsMargins()
        content_w = left + right + cols * self.CARD_W + max(0, cols - 1) * self.SPACING
        self.grid_host.setFixedWidth(content_w)

        for i, note in enumerate(self._notes):
            card = NoteCard(note)
            card.setFixedWidth(self.CARD_W)

            card.clicked.connect(self._on_card_clicked)
            card.double_clicked.connect(self._on_card_double_clicked)

            r = i // cols
            c = i % cols
            self.grid.addWidget(card, r, c)
            self._cards.append(card)

        self.grid.setRowStretch((len(self._notes) // cols) + 1, 1)

    def _calc_cols(self) -> int:
        w = self.scroll.viewport().width()
        cols = max(1, (w + self.SPACING) // (self.CARD_W + self.SPACING))
        return int(min(cols, self.MAX_COLS))
    
    def resizeEvent(self, event):
        # dialog 開著就不要重排
        if self._active_note_dlg is not None:
            super().resizeEvent(event)
            return

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
            c.set_selected(c.note.id is not None and int(c.note.id) == self._selected_note_id)

    def _on_add_clicked(self):
        self._open_note_dialog(note=None)

    def _on_card_double_clicked(self, note: Note):
        print("DOUBLE CLICK fired for", note.id)
        if note.id is None:
            return
        self._open_note_dialog(note=note)

    def _open_note_dialog(self, note: Note | None):
        if time.time() < self._block_clicks_until:
            return

        # ✅ 全 app 的 modal guard：只要已有 modal，就不要再開
        if QApplication.activeModalWidget() is not None:
            # 有人已經開著 dialog（可能是別的 NotesPage instance）
            return

        # ✅ 本 page 的 guard（保留）
        if self._active_note_dlg is not None:
            try:
                self._active_note_dlg.raise_()
                self._active_note_dlg.activateWindow()
            except Exception:
                pass
            return

        if note is None:
            dlg = NoteDialog(self, title="", content="", note_id=None)
            dlg.saved.connect(self._create_note_and_reload)
        else:
            dlg = NoteDialog(self, title=note.title, content=note.content, note_id=int(note.id))
            dlg.saved.connect(lambda t, c: self._update_note_and_reload(int(note.id), t, c))
            dlg.deleted.connect(self._delete_note_and_reload)

        self._active_note_dlg = dlg
        dlg.finished.connect(lambda _=None: setattr(self, "_active_note_dlg", None))
        dlg.exec()
        self._block_clicks_until = time.time() + 0.25


    def _create_note_and_reload(self, title: str, content: str):
        self.repo.create_note(title, content)
        self.reload_notes()

    def _update_note_and_reload(self, note_id: int, title: str, content: str):
        self.repo.update_note(note_id, title=title, content=content)
        self.reload_notes()

    def _delete_note_and_reload(self, note_id: int):
        self.repo.delete_note(note_id)
        self.reload_notes()
