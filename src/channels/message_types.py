
from datetime import datetime, timezone
from typing import Any, Dict, Generic, TypeVar
from dataclasses import dataclass, field

@dataclass(slots=True)
class OutboundMessage:
    """
    message sent to a channel
    """
    recipient: str 
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SendResult:
    """
    message received from a channel
    """
    provider: str
    recipient: str
    provider_message_id: str | None = None
    raw_response: Dict[str, Any] | None = None

