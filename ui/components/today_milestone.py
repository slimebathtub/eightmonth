from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt

class TodayMilestoneCard(QFrame):
    done_toggled = Signal(bool)  # new_is_done

    def __init__(self, milestone_title: str, task_title: str, due_text: str, is_done: bool):
        super().__init__()
        self.setObjectName("TodayMilestoneCard")

        self._is_done = bool(is_done)

        # widgets
        self.title_label = QLabel(milestone_title)
        self.sub_label = QLabel(f"from: {task_title}")
        self.due_label = QLabel(f"due: {due_text}")

        self.sub_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.65);")
        self.due_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.65);")

        # layout
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        text_col.addWidget(self.title_label)
        text_col.addWidget(self.sub_label)
        text_col.addWidget(self.due_label)

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)
        root.addLayout(text_col)

        # style
        self.setStyleSheet("""
            QFrame#TodayMilestoneCard {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
            }
            QFrame#TodayMilestoneCard:hover {
                border: 1px solid rgba(255,255,255,0.16);
                background: rgba(255,255,255,0.06);
            }
        """)

        self._apply_done_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_done = not self._is_done
            self._apply_done_style()
            self.done_toggled.emit(self._is_done)
        super().mousePressEvent(event)

    def _apply_done_style(self):
        # strikeout
        f = self.title_label.font()
        f.setStrikeOut(self._is_done)
        self.title_label.setFont(f)

        # dim title
        if self._is_done:
            self.title_label.setStyleSheet(
                "font-size: 15px; font-weight: 600; color: rgba(255,255,255,0.5);"
            )
        else:
            self.title_label.setStyleSheet(
                "font-size: 15px; font-weight: 600; color: rgba(255,255,255,1);"
            )
