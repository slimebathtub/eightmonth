from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QScrollArea, QPushButton, QMessageBox, QInputDialog,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate

from data.relax_repo import RelaxRepository


class RelaxCard(QFrame):
    toggled = Signal(int, str, bool)  # relax_id, title, checked

    def __init__(self, relax_id: int, title: str, checked: bool):
        super().__init__()
        with open("ui/style/today.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
        self.relax_id = relax_id
        self.title = title
        self._checked = checked
        self.setObjectName("RelaxCard")
        self.ui()
        self.set_checked(checked)

    def ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 12, 0, 12)

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("font-size: 16px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(180, 50)
        self.setMaximumSize(240, 58)
        self.setStyleSheet("padding:0px;") 
        
        root.addWidget(self.title_label,1)

    def set_checked(self, checked: bool):
        self._checked = checked
        self.setProperty("selected", "true" if checked else "false")
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            new_checked = not self._checked
            self.toggled.emit(self.relax_id, self.title, new_checked)
        super().mousePressEvent(event)


class RelaxListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.relax_repo = RelaxRepository()
        self.ui()
        self.reload_relax_items()

    def ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self.btn_add_relax = QPushButton("")
        self.btn_add_relax.setObjectName("AddRelax")
        self.btn_add_relax.clicked.connect(self._on_add_relax)
        root.addWidget(self.btn_add_relax)

        self.relax_list_container = QWidget()
        self.relax_list_layout = QVBoxLayout(self.relax_list_container)
        self.relax_list_layout.setContentsMargins(0, 0, 0, 0)
        self.relax_list_layout.setSpacing(8)

        relax_scroll = QScrollArea()
        relax_scroll.setWidgetResizable(True)
        relax_scroll.setFrameShape(QScrollArea.NoFrame)
        relax_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        relax_scroll.setWidget(self.relax_list_container)
        relax_scroll.setStyleSheet("background: transparent;")

        root.addWidget(relax_scroll)
        

    def _today_str(self) -> str:
        return QDate.currentDate().toString("yyyy-MM-dd")

    def _clear_relax_list(self):
        while self.relax_list_layout.count():
            item = self.relax_list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def reload_relax_items(self):
        self._clear_relax_list()
        date_str = self._today_str()

        relax_rows = self.relax_repo.list_relax_items()
        selected_ids = self.relax_repo.list_today_relax_ids(date_str)

        for r in relax_rows:
            rid = int(r["id"])
            title = r["title"]
            checked = (rid in selected_ids)

            card = RelaxCard(rid, title, checked)
            card.toggled.connect(self._on_card_toggled)
            self.relax_list_layout.addWidget(card)

        self.relax_list_layout.addStretch(1)

    def _on_card_toggled(self, relax_id: int, title: str, checked: bool):
        date_str = self._today_str()

        if checked:
            ok = QMessageBox.question(
                self, "Add to Today", f"Add '{title}' to today's schedule?"
            ) == QMessageBox.Yes
            if ok:
                self.relax_repo.add_to_today(date_str, relax_id)
            # 不管按 Yes/No 都 reload，把 UI 還原成真實狀態
            self.reload_relax_items()
            return

        # checked == False → remove
        ok = QMessageBox.question(
            self, "Remove from Today", f"Remove '{title}' from today's schedule?"
        ) == QMessageBox.Yes
        if ok:
            self.relax_repo.remove_from_today(date_str, relax_id)
        self.reload_relax_items()

    def _on_add_relax(self):
        title, ok = QInputDialog.getText(self, "Add Relax", "Relax title:")
        if not ok:
            return

        try:
            self.relax_repo.add_relax_item(title)
        except Exception as e:
            QMessageBox.warning(self, "Add failed", str(e))
            return

        self.reload_relax_items()
