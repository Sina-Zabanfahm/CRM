from pydantic import BaseModel, Field
import pytest

from src.config.app_config import get_app_config
from src.executions.parser.simple_pydantic_extractor import SimplePydanticExtractor

from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact

from src.executions.input_kinds import InputKinds
from src.models.llm_factory import LLMFactory


class PersonSchema(BaseModel):
    name: str 
    age: int


def extractor_test():
    state =ExecutionState()
    run_id = "execution_test"
    
    config = get_app_config()
    llm = LLMFactory.create_from_config(config.llm_configs[0])
    
    text_artifact = Artifact[str](
        kind= InputKinds.TEXT.value,
        content="john is 45 years old",
        name = "content"
    )
    state.artifacts[run_id] = {
        "content": text_artifact
    }
    execution = SimplePydanticExtractor(llm, PersonSchema)

    outputs = execution.run(state, run_id)

    assert outputs is not None

    

extractor_test()