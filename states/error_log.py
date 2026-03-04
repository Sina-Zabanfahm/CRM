
from datetime import datetime, timezone
from typing import Any, Dict
from dataclasses import dataclass, field

@dataclass(frozen = True)
class ErrorLog:
    tool: str
    message:str
    stack: str
    created_at: datetime  = field(default_factory= lambda:
                                 datetime.now(timezone.utc))