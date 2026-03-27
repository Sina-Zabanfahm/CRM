import asyncio

from src.executions.fetch.fetch_execution import FetchExecution
from src.executions.fingerprint.finger_print_execution import FingerprintExecution
from src.executions.gating.llm_gate_execution import LlmGateExecution
from src.executions.input_kinds import InputKinds
from src.executions.normalize.normalize_execution import NormalizeExecution
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource


async def main():
    state = ExecutionState()
    run_id = "llm_gate_manual_test"

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

    state.artifacts[run_id] = {
        "web_resource": fetched_artifact
    }

    normalize_execution = NormalizeExecution()
    normalized_artifacts = await normalize_execution.aexecute(
        state,
        run_id,
        state.artifacts[run_id],
    )

    state.artifacts[run_id] = {
        "web_resource": normalized_artifacts[0]
    }

    fingerprint_execution = FingerprintExecution()
    fingerprinted_artifact = await fingerprint_execution.aexecute(
        state,
        run_id,
        state.artifacts[run_id],
    )

    state.artifacts[run_id] = {
        "web_resource": fingerprinted_artifact
    }

    llm_gate_execution = LlmGateExecution()
    gated_artifact = await llm_gate_execution.aexecute(
        state,
        run_id,
        state.artifacts[run_id],
    )

    print(gated_artifact.content.should_pass_to_llm)


if __name__ == "__main__":
    asyncio.run(main())
