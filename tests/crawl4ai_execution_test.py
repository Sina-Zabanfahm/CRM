import uuid

from src.executions.crawler.crawl4ai_exection import Crawl4AIExecution

from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact

from src.executions.input_kinds import InputKinds

def test_crawl4ai_execution():

    state = ExecutionState()
    run_id = "test_run"

    url_artifact = Artifact[str](
        id=str(uuid.uuid4()),
        kind= InputKinds.TEXT.value,
        name="url",
        content="https://github.com/Sina-Zabanfahm/Fin_AT"
    )

    state.artifacts[run_id] = {
        "url": url_artifact
    }

    execution = Crawl4AIExecution()

    outputs = execution.run(state, run_id)

    for artifact in outputs:
        print("Artifact ID:", artifact.id)
        print("Kind:", artifact.kind)
        print("Name:", artifact.name)
        print("Content preview:", artifact.content[:500])

    assert artifact is not None


test_crawl4ai_execution()