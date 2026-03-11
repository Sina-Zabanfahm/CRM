from __future__ import annotations

import asyncio
from typing import Any

import requests
from playwright.async_api import async_playwright

from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState


# Fetch a document from a URL, fall back to Playwright on TLS or request failures,
# and detect the coarse file type from headers or magic bytes without parsing.
class DocumentFetchExecution(BaseExecution):
    input_spec = (InputSpec(role="url", kind=InputKinds.TEXT.value),)

    async def aexecute(
        self,
        state: ExecutionState,
        run_id: str,
        inputs: dict[str, Artifact[Any]],
    ) -> Artifact:
        raise NotImplementedError("")
    