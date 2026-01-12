from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional
import uuid

ProgressMode = Literal["auto", "manual"]

def new_id() -> str:
    return str(uuid.uuid4())

@dataclass
class Milestone:
    title: str
    done: bool = False
    description: str = ""
    due_date: Optional[str] = None
    sort_order: int = 0
    id: Optional[int] = None   # 對應 DB AUTOINCREMENT，可為 None

@dataclass
class Task:
    title: str
    priority: int = 3
    progress_mode: ProgressMode = "auto"
    progress_manual: int = 0
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    milestones: list[Milestone] = field(default_factory=list)
    id: str = field(default_factory=new_id)

    @property
    def progress(self) -> int:
        if self.progress_mode == "manual":
            try:
                v = int(self.progress_manual)
            except (TypeError, ValueError):
                v = 0
            return max(0, min(100, v))

        if not self.milestones:
            return 0
        total = len(self.milestones)
        done = sum(1 for m in self.milestones if m.done)
        return int(round(done / total * 100))
