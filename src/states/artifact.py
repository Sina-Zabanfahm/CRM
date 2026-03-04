
from datetime import datetime, timezone
from typing import Any, Dict, Generic, TypeVar
from dataclasses import dataclass, field
T = TypeVar("T")
@dataclass(frozen = True, slots = True)
class Artifact(Generic[T]):

    id: str
    kind: str
    name: str 
    content: T
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory= lambda:
                                 datetime.now(timezone.utc))
    
