
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.states.web_resources import ResourceKind


dataclass(slots =True)
class ResourceRecord:
    url: str
    final_url: str | None = None
    kind: ResourceKind = ResourceKind.UNKNOWN
    content_kind: str | None = None

    last_crawled_at : datetime = field(
        default_factory = lambda : datetime.now(timezone.utc)
    )

    body_sha256: str | None = None
    text_sha256: str | None = None
    simhas: str | None = None 
