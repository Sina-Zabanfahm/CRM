import asyncio

from src.executions.fetch.fetch_execution import FetchExecution
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource


async def main():
    state = ExecutionState()
    run_id = "fetch_manual_test"

    resource = WebResource(
        url="https://pub-calgary.escribemeetings.com/filestream.ashx?DocumentId=352749",
        content=None,
    )

    state.artifacts[run_id] = {
        "web_resource": Artifact(
            id=run_id,
            kind=InputKinds.WEBRESOURCE.value,
            name="web_resource",
            content=resource,
        )
    }

    execution = FetchExecution(timeout=30)
    out_artifact = await execution.aexecute(state, run_id, state.artifacts[run_id])

    print("Artifact.kind:", out_artifact.kind)
    print("URL:", out_artifact.content.url)
    print("Final URL:", out_artifact.content.final_url)
    print("Kind:", out_artifact.content.kind)
    print("Content-Type:", out_artifact.content.content_type)
    print("Status:", out_artifact.content.status_code)
    print("Body bytes:", None if out_artifact.content.body is None else len(out_artifact.content.body))
    print("Error:", out_artifact.content.error)


if __name__ == "__main__":
    asyncio.run(main())