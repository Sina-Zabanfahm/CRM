import asyncio
from io import BytesIO

from pypdf import PdfWriter

from src.executions.fetch.fetch_execution import FetchExecution
from src.executions.normalize.normalize_execution import NormalizeExecution
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import ResourceKind, WebResource


def build_blank_pdf(page_count: int = 2) -> bytes:
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=72, height=72)

    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_normalize_pdf_returns_page_artifacts():
    state = ExecutionState()
    run_id = "normalize_pdf_pages_test"

    resource = WebResource(
        url="https://example.com/document.pdf",
        kind=ResourceKind.PDF,
        body=build_blank_pdf(page_count=2),
    )

    state.artifacts[run_id] = {
        "web_resource": Artifact(
            id=run_id,
            kind=InputKinds.WEBRESOURCE.value,
            name="web_resource",
            content=resource,
        )
    }

    normalized_artifacts = asyncio.run(NormalizeExecution().arun(state, run_id))

    assert len(normalized_artifacts) == 2
    assert normalized_artifacts[0].content.url.endswith("#page=1")
    assert normalized_artifacts[1].content.url.endswith("#page=2")
    assert normalized_artifacts[0].content.meta_data["page_number"] == 1
    assert normalized_artifacts[1].content.meta_data["page_number"] == 2


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
    normalized_artifacts = await normalize_execution.aexecute(
        state,
        run_id,
        state.artifacts[run_id],
    )
    print("\nAfter normalize")
    print("  artifacts:", len(normalized_artifacts))
    for index, normalized_artifact in enumerate(normalized_artifacts, start=1):
        content = normalized_artifact.content.content
        preview = None if content is None else content
        print(f"  page {index} kind:", normalized_artifact.content.kind)
        print(f"  page {index} content length:", None if content is None else len(content))
        print(f"  page {index} preview:", preview)
        print(f"  page {index} error:", normalized_artifact.content.error)


if __name__ == "__main__":
    asyncio.run(main())
