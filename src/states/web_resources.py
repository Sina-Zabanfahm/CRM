from datetime import datetime, timezone
from typing import Any, Dict, Generic, TypeVar
from dataclasses import dataclass, field

@dataclass(slots = True)
class WebResource:
    url: str 
    final_url: str | None = None
    kind: str | None = None
    content_type: str | None = None
    status_code: str | None = None 
    body: bytes | None = None 
    content: str | None = None
    error: str | None = None 
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))