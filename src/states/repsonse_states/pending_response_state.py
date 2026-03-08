
from typing import Any
from datetime import datetime, timezone
from dataclasses import dataclass, field

@dataclass(slots = True)
class PendingResponseState:
    run_id: str 
    provider: str
    recipient: str
    status: str 
    created_at: datetime = field(default_factory= lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)