from __future__ import annotations
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from core.module.Task import Milestone


class MilestoneListWidget(QListWidget):
    # 自訂訊號：拖曳排序後通知外層回寫 DB
    order_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 拖曳排序
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

        # 用 checkbox
        self.setSelectionMode(QListWidget.SingleSelection)

        # rowsMoved 是 model 的訊號
        self.model().rowsMoved.connect(lambda *args: self.order_changed.emit())

    def set_milestones(self, milestones: list[Milestone]):
        self.blockSignals(True)
        self.clear()

        for m in milestones:
            it = QListWidgetItem(m.title)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)
            it.setCheckState(Qt.Checked if m.done else Qt.Unchecked)

            # 把 milestone id 和其他資料存在 item
            it.setData(Qt.UserRole, m.id)
            it.setData(Qt.UserRole + 1, m.description)
            it.setData(Qt.UserRole + 2, m.due_date)
            self.addItem(it)

        self.blockSignals(False)

    def milestones_in_ui_order(self) -> list[dict]:
        """回傳目前 UI 上的順序（給你回寫 sort_order 用）"""
        out = []
        for i in range(self.count()):
            it = self.item(i)
            out.append({
                "id": it.data(Qt.UserRole),
                "title": it.text(),
                "done": it.checkState() == Qt.Checked,
                "description": it.data(Qt.UserRole + 1) or "",
                "due_date": it.data(Qt.UserRole + 2),
                "sort_order": i,
            })
        return out
