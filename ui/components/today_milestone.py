from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class TodayMilestoneCard(QFrame):
    def __init__ (self, milestone_title: str, task_title: str, due_text: str):
        super().__init__()
        self.setObjectName("TodayMilestoneCard")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(2)

        title = QLabel(milestone_title)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")

        task_name = QLabel(f"from: {task_title}")
        task_name.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.65);")

        due = QLabel(f"due: {due_text}")
        due.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.65);")

        root.addWidget(title)
        root.addWidget(task_name)
        root.addWidget(due)


        self.setStyleSheet("""
            QFrame#TodayMilestoneRow {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
            }
            QFrame#TodayMilestoneRow:hover {
                border: 1px solid rgba(255,255,255,0.16);
                background: rgba(255,255,255,0.06);
            }
        """)


    
    

