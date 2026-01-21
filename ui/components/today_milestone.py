from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt


class TodayMilestoneCard(QFrame):
    done_toggled = Signal(bool)  # new_is_done

    def __init__(self, milestone_title: str, task_title: str, due_text: str, is_done: bool):
        super().__init__()
        with open("ui/style/today.qss", "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

        self.setObjectName("TodayMilestoneCard")
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._is_done = bool(is_done)

        # widgets
        self.title_label = QLabel(milestone_title)
        self.title_label.setStyleSheet("font-size: 18px; color: white;")
        self.sub_label = QLabel(f"from: {task_title}")
        #self.due_label = QLabel(f"due: {due_text}")
        self.setFixedHeight(120)

        self.sub_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.65);")
        #self.due_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.65);")

        # layout
        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        #text_col.setSpacing(2)
        text_col.addWidget(self.title_label)
        text_col.addWidget(self.sub_label)
        #text_col.addWidget(self.due_label)

        root = QHBoxLayout(self)
        root.addLayout(text_col)
        root.setContentsMargins(50, 25, 30, 25)
        root.setSpacing(0)

        

        self._apply_done_style()
        #self.setStyleSheet("background: rgb(255,0,0); border: 3px solid lime;")
        from PySide6.QtWidgets import QApplication
        print("card local ss len =", len(self.styleSheet()))
        print("app ss len        =", len(QApplication.instance().styleSheet()))


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_done = not self._is_done
            self._apply_done_style()
            self.done_toggled.emit(self._is_done)
        super().mousePressEvent(event)

    def _apply_done_style(self):
        f = self.title_label.font()
        f.setStrikeOut(self._is_done)
        self.title_label.setFont(f)

        # ✅ 永遠 setProperty（true/false 都要）
        self.setProperty("done", "true" if self._is_done else "false")

        # ✅ 強制重新套用 style
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


