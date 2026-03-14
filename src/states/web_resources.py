from typing import Any
from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, field

class ResourceKind(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    PDF = "pdf"
    MARKDOWN = "markdown"
    UNKNOWN = "unknown"

class MetaDataKind(str, Enum):
    CRAWL4AI = "crawl4ai"
    PLAYWRIGHT = "playwright"
    REQUESTS = "requests"

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
    meta_data: dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def target_url(self):
        return self.final_url if self.final_url is not None else self.url