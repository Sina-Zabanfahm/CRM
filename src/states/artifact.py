
from datetime import datetime, timezone
from typing import Any, Dict, Generic, TypeVar
from dataclasses import dataclass, field

T = TypeVar("T")

@dataclass(frozen = True, slots = True)
class Artifact(Generic[T]):
    content: T
    id: str | None = None
    name: str | None = None
    kind: str | None = None 

    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory= lambda:
                                 datetime.now(timezone.utc))
    
