from __future__ import annotations

import asyncio
from dataclasses import replace
from typing import Any

from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.persistence.resource_record import ResourceRecord
from src.persistence.resource_repository import ResourceRepository
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource


class LlmGateExecution(BaseExecution):
    input_spec = (
        InputSpec(role="web_resource", kind=InputKinds.WEBRESOURCE.value),
    )

    def __init__(
        self,
        repository: ResourceRepository | None = None,
        name: str | None = None,
        id: str | None = None,
    ):
        super().__init__(name, id)
        self.repository = repository or ResourceRepository()

    async def aexecute(
        self,
        state: ExecutionState,
        run_id: str,
        inputs: dict[str, Artifact[Any]],
    ) -> Artifact[WebResource]:
        resource: WebResource = inputs["web_resource"].content
        gated_resource = await asyncio.to_thread(self._gate_resource, resource)

        return Artifact(
            id=self.id,
            kind=InputKinds.WEBRESOURCE.value,
            name=self.name,
            content=gated_resource,
        )

    def _gate_resource(self, resource: WebResource) -> WebResource:
        current_record = ResourceRecord.from_web_resource(
            resource,
            body_sha256=resource.fingerprints.byte_sha,
            text_sha256=resource.fingerprints.text_sha,
            simhash=(
                str(resource.fingerprints.simhash)
                if resource.fingerprints.simhash is not None
                else None
            ),
        )

        existing_record = self.repository.get(current_record.url)

        should_pass_to_llm = (
            existing_record is None
            or self._has_content_changed(existing_record, current_record)
        )

        if should_pass_to_llm:
            self.repository.upsert(current_record)

        return replace(resource, should_pass_to_llm=should_pass_to_llm)

    @staticmethod
    def _has_content_changed(
        existing_record: ResourceRecord,
        current_record: ResourceRecord,
    ) -> bool:
        if (
            current_record.text_sha256 is not None
            and existing_record.text_sha256 is not None
        ):
            return current_record.text_sha256 != existing_record.text_sha256

        if (
            current_record.body_sha256 is not None
            and existing_record.body_sha256 is not None
        ):
            return current_record.body_sha256 != existing_record.body_sha256

        return True
