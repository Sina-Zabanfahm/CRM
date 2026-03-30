
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
    def __init__(self, name:str| None = None , id:str | None = None,
                 page_batch_size: int = 10, page_overlap: int = 1):
        super().__init__(name, id)
        self.page_batch_size = page_batch_size
        self.page_overlap = page_overlap

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
            return self._pdf_to_pages(resource, self.page_batch_size, self.page_overlap)
        except Exception as exc:
            return [replace(resource, error=str(exc))]

    @staticmethod
    def _pdf_to_pages(resource: WebResource,
                      batch_size: int,
                      overlap: int) -> list[WebResource]:
        if batch_size < 1:
            raise ValueError("page_batch_size must be at least 1")
        if overlap < 0:
            raise ValueError("page_overlap must be 0 or greater")
        if overlap >= batch_size:
            raise ValueError("page_overlap must be smaller than page_batch_size")

        body = resource.body
        if body is None:
            return [resource]
        reader = PdfReader(BytesIO(body))
        page_resources: list[WebResource] = []
        source_url = resource.url
        source_final_url = resource.final_url
        pages = reader.pages
        num_pages = len(pages)
        step = batch_size - overlap

        for idx in range(0, num_pages, step):
            end_idx = min(idx + batch_size, num_pages)
            start_page = idx + 1
            end_page = end_idx
            page_numbers = list(range(start_page, end_page + 1))
            page_ref = (
                f"page={start_page}"
                if len(page_numbers) == 1
                else f"pages={start_page}-{end_page}"
            )

            chunk_pages = pages[idx: end_idx]
            chunk_text = "\n".join(page.extract_text() or "" 
                                   for page in chunk_pages)
            page_resources.append(
                replace(
                    resource,
                    url=f"{source_url}#{page_ref}",
                    final_url=(
                        f"{source_final_url}#{page_ref}"
                        if source_final_url is not None
                        else None
                    ),
                    body=None,
                    content=chunk_text,
                    meta_data={
                        **resource.meta_data,
                        "source_url": source_url,
                        "source_final_url": source_final_url,
                        "page_number": page_numbers[0] if len(page_numbers) == 1 else page_numbers,
                        "page_numbers": page_numbers,
                    },
                )
            )
            if end_idx == num_pages:
                break

        return page_resources or [resource]
