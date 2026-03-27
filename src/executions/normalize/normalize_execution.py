
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

    async def aexecute(self, state, run_id, inputs) -> list[Artifact[WebResource]]:
        resource = inputs["web_resource"].content
        normalized_resources = await asyncio.to_thread(self._normalize_content, resource)

        return [
            Artifact(
                id=self.id,
                kind=InputKinds.WEBRESOURCE.value,
                name=self.name,
                content=normalized_resource,
            )
            for normalized_resource in normalized_resources
        ]
    
    #incomplete for now - only changing pdf to text
    def _normalize_content(self, resource: WebResource) -> list[WebResource]:
        if resource.content is not None and len(resource.content) >= 3:
            return [resource]
        if resource.kind != ResourceKind.PDF:
            return [resource]

        try:
            return self._pdf_to_pages(resource)
        except Exception as exc:
            return [replace(resource, error=str(exc))]

    @staticmethod
    def _pdf_to_pages(resource: WebResource) -> list[WebResource]:
        body = resource.body
        if body is None:
            return [resource]
        reader = PdfReader(BytesIO(body))
        page_resources: list[WebResource] = []
        source_url = resource.url
        source_final_url = resource.final_url

        for page_number, page in enumerate(reader.pages, start=1):
            page_resources.append(
                replace(
                    resource,
                    url=f"{source_url}#page={page_number}",
                    final_url=(
                        f"{source_final_url}#page={page_number}"
                        if source_final_url is not None
                        else None
                    ),
                    body=None,
                    content=page.extract_text() or "",
                    meta_data={
                        **resource.meta_data,
                        "source_url": source_url,
                        "source_final_url": source_final_url,
                        "page_number": page_number,
                    },
                )
            )

        return page_resources or [resource]
