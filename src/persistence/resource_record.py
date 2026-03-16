
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.states.web_resources import ResourceKind, WebResource


@dataclass(slots=True)
class ResourceRecord:
    url: str
    final_url: str | None = None
    kind: ResourceKind = ResourceKind.UNKNOWN
    content_type: str | None = None

    last_crawled_at : datetime = field(
        default_factory = lambda : datetime.now(timezone.utc)
    )

    body_sha256: str | None = None
    text_sha256: str | None = None
    simhash: str | None = None

    @classmethod
    def from_web_resource(
        cls,
        resource: WebResource,
        *,
        body_sha256: str | None = None,
        text_sha256: str | None = None,
        simhash: str | None = None,
        last_crawled_at: datetime | None = None,
    ) -> "ResourceRecord":
        return cls(
            url=resource.url,
            final_url=resource.final_url,
            kind=resource.kind,
            content_type=resource.content_type,
            last_crawled_at=last_crawled_at or datetime.now(timezone.utc),
            body_sha256=body_sha256,
            text_sha256=text_sha256,
            simhash=simhash,
        )
