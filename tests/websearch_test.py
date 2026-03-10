from src.executions.search.web_search_execution import WebSearchExecution
from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact
from src.executions.input_kinds import InputKinds


def test_web_search_execution():
    state = ExecutionState()
    run_id = "web_search_test"

    query_artifact = Artifact[str](
        id=run_id,
        kind=InputKinds.TEXT.value,
        name="query",
        content="Toronto housing procurement opportunities",
    )

    state.artifacts[run_id] = {
        "query": query_artifact
    }

    execution = WebSearchExecution(n_results=5, max_depth=1)
    outputs = execution.run(state, run_id)

    

    content = outputs.content
    assert len(content) > 0

    
    print(content)
    

if __name__ == "__main__":
    test_web_search_execution()