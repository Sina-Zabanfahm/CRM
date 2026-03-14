
import asyncio
from typing import Any

import requests
from dataclasses import replace

from src.executions.base_execution import (BaseExecution,
                                           InputSpec)
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.execution_state import ExecutionState
from src.states.web_resources import ResourceKind, WebResource

#Fetch Response metadata and bytes
class FetchExecution(BaseExecution):
    input_spec = (
        InputSpec(role = "web_resource", kind = InputKinds.WEBRESOURCE.value),
    )

    def __init__(self, name = None, id = None, timeout: int = 30):
        self.timeout = timeout
        super().__init__(name, id)

    async def aexecute(self, state, run_id, inputs):
        resource = inputs["web_resource"].content
        pass

    def _fetch_resource(self, resource: WebResource) -> WebResource:
        pass

    def _fetch_full_body(self, resource: WebResource):
        try:
            with requests.get(
                resource.url,
                allow_redirects= True,
                timeout = self.timeout
            ) as response:
                response.raise_for_status()
                return replace(
                        resource,
                        content_type=response.headers.get("Content-Type"),
                        status_code=response.status_code,
                        body=response.content,
                        error=None,
                    )
        except requests.RequestException as exc:
            return replace(resource, error = str(exc) )
