import json
from typing import List, Literal, Optional, Any

from pydantic import BaseModel, Field

from src.executions.crawler.crawl4ai_deep_execution import Crawl4aiDeepCrawl
from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact
from src.executions.input_kinds import InputKinds
from src.config.app_config import get_app_config
from src.models.llm_factory import LLMFactory
from src.executions.parser.simple_pydantic_extractor import SimplePydanticExtractor


class ProcurementSignal(BaseModel):
    signal_type: Literal[
        "RFP",
        "Pre-RFP",
        "RFQ",
        "Tender",
        "EOI",
        "Notice",
        "Addendum",
        "Award",
        "Unknown"
    ] = Field(..., description="Type of procurement-related signal found in the markdown.")

    title: str = Field(..., description="Title of the opportunity or notice.")
    issuer: Optional[str] = Field(None, description="Organization, municipality, or agency issuing the notice.")
    due_date: Optional[str] = Field(None, description="Submission or closing date if present.")
    posting_date: Optional[str] = Field(None, description="Posting date if present.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this extraction.")


class ProcurementSignalCollection(BaseModel):
    signals: List[ProcurementSignal] = Field(
        default_factory=list,
        description="List of procurement-related signals extracted from the cleaned markdown."
    )


def crawl(url: str) -> Any:
    state = ExecutionState()
    run_id = "test_run"

    url_artifact = Artifact[str](
        id=run_id,
        kind=InputKinds.TEXT.value,
        name="url",
        content=url,
    )

    state.artifacts[run_id] = {
        "url": url_artifact
    }

    execution = Crawl4aiDeepCrawl(max_depth=0)
    output = execution.run(state, run_id)
    input(output)
    return output[0].content


def extract(content: str):
    state = ExecutionState()
    run_id = "execution_test"

    config = get_app_config()
    llm = LLMFactory.create_from_config(config.llm_configs[1])

    text_artifact = Artifact[str](
        id=run_id,
        kind=InputKinds.TEXT.value,
        content=content,
        name="content",
    )

    state.artifacts[run_id] = {
        "content": text_artifact
    }

    execution = SimplePydanticExtractor(llm, ProcurementSignalCollection)
    outputs = execution.run(state, run_id)
    return outputs


def flatten_texts(obj: Any) -> list[str]:
    results: list[str] = []

    if isinstance(obj, str):
        results.append(obj)

    elif isinstance(obj, list):
        for item in obj:
            results.extend(flatten_texts(item))

    elif isinstance(obj, dict):
        for value in obj.values():
            results.extend(flatten_texts(value))

    return results


def crawl_and_extract_all(url: str, save_path: str):
    texts:dict = crawl(url)
    
    tot = {}
    index = 0
    for key, val in texts.items():
        for text in val:
            resp = extract(text)
            tot[index] = resp[0].content.model_dump()
            index+=1

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(tot, f, indent=2, ensure_ascii=False)

    return tot


if __name__ == "__main__":
    result = crawl_and_extract_all(
        url="https://torontohousing.ca/partner-tchc/procurement-opportunities?utm_source=chatgpt.com",
        save_path="procurement_signals1.json",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))