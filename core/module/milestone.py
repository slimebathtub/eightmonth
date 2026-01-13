from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional
import uuid

@dataclass
class Milestone:
    title: str
    done: bool = False
    description: str = ""
    due_date: Optional[str] = None
    sort_order: int = 0
    id: Optional[int] = None