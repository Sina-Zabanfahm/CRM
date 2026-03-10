from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState


class LoadJsonExecution(BaseExecution):
    input_spec = (
        InputSpec(role="path", kind=InputKinds.TEXT.value),
    )

    async def aexecute(
        self,
        state: ExecutionState,
        run_id: str,
        inputs: dict[str, Artifact],
    ) -> list[Artifact]:
        path_str = inputs["path"].content
        path = Path(path_str)

        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        data = await asyncio.to_thread(self._load_json, path)

        artifact = Artifact(
            id=self.id,
            kind="json",
            name=path.stem,
            content=data,
        )
        return [artifact]

    @staticmethod
    def _load_json(path: Path) -> Any:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)