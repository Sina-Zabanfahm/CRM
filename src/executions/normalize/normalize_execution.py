
import asyncio
from dataclasses import replace
from io import BytesIO
from pypdf import PdfReader

from src.executions.base_execution import (BaseExecution, InputSpec)
from src.states.execution_state import ExecutionState
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.web_resources import WebResource, ResourceKind

class NormalizeExecution(BaseExecution):

    input_spec = (InputSpec(role = "web_resource", kind = InputKinds.WEBRESOURCE.value), )

    async def aexecute(self, state, run_id, inputs) -> Artifact[WebResource]:
        resource = inputs["web_resource"].content
        normalized_res = await asyncio.to_thread(self._normalize_content, resource)

        return Artifact(
            id = self.id,
            kind = InputKinds.WEBRESOURCE.value,
            name = self.name,
            content = normalized_res
        )
    
    #incomplete for now - only changing pdf to text
    def _normalize_content(self, resource: WebResource) -> WebResource:
        if resource.content is not None and len(resource.content) >= 3:
            return resource
        if resource.kind != ResourceKind.PDF:
            return resource

        try:
            return self._pdf_to_text(resource)
        except Exception as exc:
            return replace(resource, error=str(exc))

    @staticmethod
    def _pdf_to_text(resource: WebResource) -> WebResource:
        body = resource.body
        if body is None:
            return resource  
        reader = PdfReader(BytesIO(body))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return replace(resource,
                       content = text)