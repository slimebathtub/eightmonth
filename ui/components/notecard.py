from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from core.module.note import Note
from PySide6.QtCore import Signal, Qt, QTimer

class NoteCard(QFrame):
    clicked = Signal(object)         # emits Note
    double_clicked = Signal(object)  # emits Note
    def __init__(self, note: Note):
        super().__init__()
        self.note = note

        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._emit_single_click)

        self.ui()
        self.update_view()
    
    def ui(self):
        self.setObjectName("NoteCard")
        self.setCursor(Qt.PointingHandCursor)
        CARD_W = 300
        self.setFixedWidth(CARD_W)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumHeight(120)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(6)

        self.title_label = QLabel()
        self.title_label.setObjectName("Title")

        self.preview_label = QLabel()
        self.preview_label.setObjectName("Preview")
        self.preview_label.setWordWrap(True)

        self.meta_label = QLabel()
        self.meta_label.setObjectName("Meta")

        # ✅ 讓文字不吃 mouse event，所有點擊都交給 NoteCard 自己處理
        self.title_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.preview_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.meta_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)


        root.addWidget(self.title_label)
        root.addWidget(self.preview_label, 1)
        root.addWidget(self.meta_label)

        self.setStyleSheet("""
            QFrame#NoteCard {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
            }
            QFrame#NoteCard:hover {
                border: 1px solid rgba(255,255,255,0.18);
                background: rgba(255,255,255,0.06);
            }
            QLabel#Title {
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#Preview, QLabel#Meta {
                font-size: 12px;
                color: rgba(255,255,255,0.65);
            }
            QFrame#NoteCard[selected="true"] {
                border: 1px solid rgba(255,255,255,0.45);
                background: rgba(255,255,255,0.10);
            }
        """)
    
    def update_view(self):
        title = (getattr(self.note, "title", "") or "").strip()
        content = (getattr(self.note, "content", "") or "").strip()

        if not title:
            title = "(No title)"

        # 內容預覽：最多 4 行
        lines = content.splitlines()
        preview = "\n".join(lines[:4]).strip()
        if not preview:
            preview = "(Empty)"

        updated = getattr(self.note, "updated_at", None) or ""
        # 你之後想顯示更漂亮的時間格式再處理
        meta = f"Updated: {updated}" if updated else ""

        self.title_label.setText(title)
        self.preview_label.setText(preview)
        self.meta_label.setText(meta)

    def set_selected(self, selected: bool):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def _emit_single_click(self):
        self.clicked.emit(self.note)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._click_timer.start(220)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._click_timer.isActive():
                self._click_timer.stop()
            self.double_clicked.emit(self.note)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)