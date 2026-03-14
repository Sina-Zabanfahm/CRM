from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, field
class ResourceKind(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"


@dataclass(slots = True)
class WebResource:
    url: str 
    final_url: str | None = None
    kind: ResourceKind = ResourceKind.UNKNOWN #guessed from the url
    content_type: str | None = None #From requests.response
    status_code: int | None = None 
    body: bytes | None = None 
    content: str | None = None
    error: str | None = None 
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
