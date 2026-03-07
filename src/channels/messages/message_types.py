
from datetime import datetime, timezone
from typing import Any, Dict, Generic, TypeVar
from dataclasses import dataclass, field

@dataclass(slots=True)
class OutboundMessage:
    """
    Generic message to send through a channel.
    """
    recipient: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SendResult:
    """
    Result returned after sending a message.
    """
    provider: str
    recipient: str
    provider_message_id: str | None = None
    raw_response: Dict[str, Any] | None = None

