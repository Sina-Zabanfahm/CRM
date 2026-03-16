
import asyncio

from dataclasses import replace
import hashlib

from src.executions.input_kinds import InputKinds
from src.executions.base_execution import BaseExecution, InputSpec
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource, ResourceFingerprint

class FingerprintExecution(BaseExecution):

    input_spec = (InputSpec(role = "web_resource", kind = InputKinds.WEBRESOURCE.value), )

    async def aexecute(self, state: ExecutionState, run_id, inputs) -> Artifact[WebResource]:
        resource: WebResource = inputs["web_resource"].content
        fingerprints = await asyncio.to_thread(self._compute_finger_print, resource)
        mod_resource = replace(
            resource,
            fingerprints = fingerprints
        )
        return Artifact(
            id = self.id,
            kind = InputKinds.WEBRESOURCE.value,
            name = self.name,
            content = mod_resource
        )
    

    def _compute_finger_print (self, resource: WebResource) -> ResourceFingerprint:
        return ResourceFingerprint(
            byte_sha = self._compute_byte_sha256(resource),
            text_sha = self._compute_text_sha256(resource),
            simhash = self._compute_simhash(resource)
        )
    @staticmethod
    def _compute_byte_sha256(resource: WebResource) -> str | None:
        if resource.body is None:
            return None
        return hashlib.sha256(resource.body).hexdigest()
    
    @staticmethod
    def _compute_text_sha256(resource: WebResource) -> str | None:
        if resource.content is None or len(resource.content) == 0 :
            return None
        return hashlib.sha256(resource.content.encode("utf-8")).hexdigest()
    
    @staticmethod
    def _compute_simhash(resource: WebResource) -> int | None:
        raise NotImplementedError