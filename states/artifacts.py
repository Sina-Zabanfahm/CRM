
from datetime import datetime, timezone
from typing import Any, Dict
from dataclasses import dataclass, field

@dataclass(frozen = True)
class Artifact:

    id: str
    type: str
    name: str 
    content: Any
    meta: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory= lambda:
                                 datetime.now(timezone.utc))
    
