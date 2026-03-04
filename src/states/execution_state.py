
from dataclasses import dataclass, field
from datetime import datetime, timezone
from src.states.artifact import Artifact
from src.states.error_log import ErrorLog
from src.states.event import Event

@dataclass
class ExecutionState:
    artifacts: list[Artifact] = field(default_factory=[])
    error_logs: list[ErrorLog] = field(default_factory=[])
    events: list[Event] = field(default_factory=[])
    created_at: datetime = field(default_factory= lambda:
                                 datetime.now(timezone.utc))