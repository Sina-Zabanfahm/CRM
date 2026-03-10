
import asyncio

from dataclasses import dataclass
from typing import Any, Protocol, Iterable
import uuid
from abc import ABC, abstractmethod
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState

@dataclass(frozen = True)
class InputSpec:
    role: str
    kind: str
    required: bool = True

class BaseExecution(ABC):

    name: str
    input_spec: tuple[InputSpec, ...] = ()

    def __init__(self, name:str| None = None , id:str | None = None):
        self.name = name if name is not None else self.__class__.__name__
        self.id = id if id is not None else uuid.uuid4()

    def validate_inputs(self, inputs: dict[str, Artifact[Any]]) -> None:

        for spec in self.input_spec:
            if spec.role not in inputs:
                if spec.required:
                    raise ValueError(f"{self.name}: missing required input {spec.role}")
                continue

            artifact = inputs[spec.role]
            if artifact.kind != spec.kind:
                raise TypeError(f"""{self.name}: input {spec.role} 
                                need to be of the kind {artifact.kind}
                                """)

    async def arun(self, state:ExecutionState, run_id: str) -> Artifact[Any]:
        inputs = state.artifacts.get(run_id, {})
        self.validate_inputs(inputs)
        outputs = await self.aexecute(
            state = state,
            run_id = run_id,
            inputs = inputs
        )
        return outputs

    def run(self, state: ExecutionState, run_id: str) -> Artifact[Any]:
        inputs = state.artifacts.get(run_id, {})
        self.validate_inputs(inputs)
        outputs = self.execute(
            state = state,
            run_id = run_id,
            inputs = inputs
        )
        return outputs
        
    def execute(self,
                state:ExecutionState,
                run_id: str,
                inputs: dict[str, Artifact[Any]]):

        self.verify_not_in_event_loop()
        return asyncio.run(self.aexecute(state=state, run_id=run_id, inputs=inputs))

    @abstractmethod
    async def aexecute( 
        self, 
        state: ExecutionState,
        run_id: str,
        inputs: dict[str, Artifact[Any]]
    ) -> Artifact[str]:
        raise NotImplemented(...)
    
    def verify_not_in_event_loop(self):
        try: 
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            raise RuntimeError(f"{self.name}"
                               "Cannot run inside an event loop" \
            )  