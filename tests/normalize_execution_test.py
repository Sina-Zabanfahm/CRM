import asyncio

from src.executions.fetch.fetch_execution import FetchExecution
from src.executions.normalize.normalize_execution import NormalizeExecution
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource


async def main():
    state = ExecutionState()
    run_id = "normalize_manual_test"

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

    fetch_execution = FetchExecution(timeout=30)
    fetched_artifact = await fetch_execution.aexecute(
        state,
        run_id,
        state.artifacts[run_id],
    )

    print("After fetch")
    print("  url:", fetched_artifact.content.url)
    print("  final_url:", fetched_artifact.content.final_url)
    print("  kind:", fetched_artifact.content.kind)
    print("  content_type:", fetched_artifact.content.content_type)
    print("  status_code:", fetched_artifact.content.status_code)
    print("  body bytes:", None if fetched_artifact.content.body is None else len(fetched_artifact.content.body))
    print("  error:", fetched_artifact.content.error)

    state.artifacts[run_id] = {
        "web_resource": fetched_artifact
    }

    normalize_execution = NormalizeExecution()
    normalized_artifact = await normalize_execution.aexecute(
        state,
        run_id,
        state.artifacts[run_id],
    )

    content = normalized_artifact.content.content
    preview = None if content is None else content

    print("\nAfter normalize")
    print("  kind:", normalized_artifact.content.kind)
    print("  content length:", None if content is None else len(content))
    print("  preview:", preview)
    print("  error:", normalized_artifact.content.error)


if __name__ == "__main__":
    asyncio.run(main())
