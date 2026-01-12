from typing import Literal, Optional
from dataclasses import dataclass, field

ProgressMode = Literal["auto", "manual"]

def new_id() -> str:
    import uuid
    return str(uuid.uuid4())

@dataclass
class Milestone:
    title: str
    done: bool = False
    # weight: int = 1
    description: str = ""
    due_date: Optional[str] = ""
    sort_order: int = 0

    def __init__(self, title: str, done: bool = False, description: str = "", due_date: str = ""):
        self.title = title
        self.done = done
        self.description = description
        # self.weight = weight
        self.due_date = due_date

@dataclass
class Task:
    title: str
    priority: int = 1
    milestones: list[Milestone] = field(default_factory=new_id)
    progress_mode: ProgressMode = "auto"
    progress_manual: int = 0
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    id: str = field(default_factory = new_id)

    def __init__(self, data: dict):
        self.title = data.get("title", "")
        self.priority = data.get("priority", 3)
        self.milestones = self._normalize_milestones(data.get("milestones", []))
        self.progress_mode = data.get("progress_mode", "auto")
        self.progress_manual = data.get("progress_manual", 0)
        self.start_date = data.get("start_date", "")
        self.due_date = data.get("due_date", "")

    def _normalize_milestones(self, milestones: list) -> list[Milestone]:
        normalized: list[Milestone] = []
        for m in milestones:
            if isinstance(m, Milestone):
                normalized.append(m)
            elif isinstance(m, dict):
                normalized.append(Milestone(**m))
        return normalized
        

    def progress(self) -> int:
        if self.progress_mode == "manual":
            try:
                v = int(self.progress_manual)
            except (TypeError, ValueError):
                v = 0
            return max(0, min(100, v))
        
        if not self.milestones:
            return 0
        
        total = sum( 1 for m in self.milestones)
        done = sum( 1 for m in self.milestones if m.done)
        return int(round(done / total * 100))