from PySide6.QtWidgets import QLabel, QVBoxLayout, QFrame, QSizePolicy, QHBoxLayout
from PySide6.QtCore import Signal, Qt, QTimer
from core.module.Task import Task


class TaskCard(QFrame):
    clicked = Signal(object)
    double_clicked = Signal(object)

    def __init__(self, task: Task):
        super().__init__()
        self.task = task
        self.ui()
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._emit_single_click)

    def ui(self):
        self.setObjectName("TaskCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(72)
        
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        # title and content
        mid = QVBoxLayout()
        mid.setSpacing(2)

        self.title_label = QLabel(self.task.title)
        self.title_label.setObjectName("Title")

        milestones = QLabel(f"{len(self.task.milestones)} milestones")
        milestones.setObjectName("Milestones")

        details = QLabel(self._milestone_details())
        details.setObjectName("MilestoneDetails")
        details.setWordWrap(True)
        
        priority = QLabel(f"Priority: {self.task.priority}")
        priority.setObjectName("Priority")

        self.meta = QLabel(f"{self.task.progress}%")
        self.meta.setObjectName("Meta")

        mid.addWidget(self.title_label)
        mid.addWidget(self.meta)
        mid.addWidget(milestones)
        mid.addWidget(details)
        mid.addWidget(priority)
        root.addLayout(mid, 1)


        self.setStyleSheet("""
            QFrame#TaskCard {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
            }
            QFrame#TaskCard:hover {
                border: 1px solid rgba(255,255,255,0.18);
                background: rgba(255,255,255,0.06);
            }
            QLabel#Title {
                font-size: 16px;
                font-weight: 600;
            }
            QLabel#Meta {
                font-size: 12px;
                color: rgba(255,255,255,0.65);
            }
            QLabel#MilestoneDetails {
                font-size: 12px;
                color: rgba(255,255,255,0.65);
            }
            QLabel#Arrow {
                font-size: 22px;
                color: rgba(255,255,255,0.35);
            }
            QFrame#TaskCard[selected="true"] {
                border: 1px solid rgba(255,255,255,0.45);
                background: rgba(255,255,255,0.10);
            }
        """)

    def _milestone_details(self) -> str:
        if not self.task.milestones:
            return "No milestones"
        lines = []
        for m in self.task.milestones[:3]:
            status = "[x]" if m.done else "[ ]"
            lines.append(f"{status} {m.title}")
        if len(self.task.milestones) > 3:
            lines.append(f"... +{len(self.task.milestones) - 3} more")
        return "\n".join(lines)

    def _emit_single_click(self):
        self.clicked.emit(self.task)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 單擊：延遲一下，給雙擊機會取消
            self._click_timer.start(220)
        super().mousePressEvent(event)

    def update_view(self):
        self.title_label.setText(self.task.title)
        self.meta.setText(f"{self.task.progress}%   •   Priority {self.task.priority}")

    def set_selected(self, selected: bool):
        self.setProperty("selected", selected)

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 雙擊：取消單擊，直接進編輯
            if self._click_timer.isActive():
                self._click_timer.stop()
            self.double_clicked.emit(self.task)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
    
    def _stop_click_timer(self):
        if hasattr(self, "_click_timer") and self._click_timer.isActive():
            self._click_timer.stop()

    def hideEvent(self, event):
        self._stop_click_timer()
        super().hideEvent(event)

    def closeEvent(self, event):
        self._stop_click_timer()
        super().closeEvent(event)
