from PySide6.QtWidgets import QLabel, QVBoxLayout, QFrame, QSizePolicy, QHBoxLayout
from PySide6.QtCore import Signal, Qt


class TaskCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, task: dict):
        super().__init__()
        self.task = task
        self.ui()
    

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

        title = QLabel(self.task["title"])
        title.setObjectName("Title")

        meta = QLabel(f"{self.task['progress']}%   •   Priority {self.task['priority']}")
        meta.setObjectName("Meta")

        mid.addWidget(title)
        mid.addWidget(meta)
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
            QLabel#Arrow {
                font-size: 22px;
                color: rgba(255,255,255,0.35);
            }
        """)



    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.task)
        super().mousePressEvent(event)

