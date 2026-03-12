from __future__ import annotations

from typing import Any
from urllib.parse import urlparse, parse_qs, unquote, ParseResult
from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource, ResourceKind


#Classify the next resource and decide the next extraction path
class WebResourceRoutingExecution(BaseExecution):
    input_spec = (
        InputSpec(role = "resource", kind = InputKinds.WEBRESOURCE.value),
    )

    async def aexecute( 
        self, 
        state: ExecutionState,
        run_id: str,
        inputs: dict[str, Artifact[Any]]
    ) -> Artifact[str]:
        raise NotImplemented()
    
    @staticmethod 
    def inspect_url(url: str | None) -> ResourceKind:
        url_parsed: ParseResult | None = None
        try:
            url_parsed = urlparse(url)
        except Exception as e:
            return ResourceKind.UNKNOWN

        
        pdf_score = WebResourceRoutingExecution._is_pdf_url(url_parsed)

        return ResourceKind.UNKNOWN
    @staticmethod 
    def _is_pdf_url(parsed_path: ParseResult) -> int:
        path = unquote(parsed_path.path or "").lower()
        if path.endswith(".pdf"):
            return 1
        
        query = parse_qs(parsed_path.query or "")
        for values in query.values():
            for value in values:
                if unquote(value or "").strip().lower().endswith(".pdf"):
                    return 1
        return 0
        