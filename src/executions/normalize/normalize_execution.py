
from dataclasses import replace

from src.executions.base_execution import (BaseExecution, InputSpec)
from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact
from src.states.web_resources import WebResource

class NormalizeExecution(BaseExecution):

    input_spec = (InputSpec(role = "web_resource"), )

    def aexecute(self, state, run_id, inputs):
        return super().aexecute(state, run_id, inputs)
    
    def _normalize_content(self, resource: WebResource) -> WebResource:
        pass