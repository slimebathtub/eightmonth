from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Note:
    content: str
    title: str = ""
    id: Optional[int] = None
    created_at: str | None = None
    updated_at: str | None = None
        