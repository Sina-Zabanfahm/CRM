import asyncio

from typing import Optional, Literal, List
from pydantic import BaseModel, Field

from src.config.app_config import get_app_config
from src.models.llm_factory import LLMFactory
from src.executions.parser.parallel_pydantic_extractor import ParallelPydanticExtractor
from src.executions.graphs.crawl_graph import CrawlGraph
from src.states.web_resources import CrawlTarget, WebResource
import logging
import json
import time 

class ProcurementSignal(BaseModel):
    signal_type: Literal[
        "RFP",
        "Pre-RFP",
        "RFQ",
        "Tender",
        "EOI",
        "Notice",
        "Addendum",
        "Unknown"
        
    ] = Field(..., description="Type of procurement-related signal found in the markdown. Or signals that lead and can " \
    "deduce procurement related.")

    title: str = Field(..., description="Title of the opportunity or notice.")
    description: str = Field(..., description="Description of the offering")
    issuer: Optional[str] = Field(None, description="Organization, municipality, or agency issuing the notice.")
    due_date: Optional[str] = Field(None, description="Submission or closing date if present.")
    posting_date: Optional[str] = Field(None, description="Posting date if present.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this extraction.")
    budget: Optional[float] = Field(0, description="Allocated budget")


class ProcurementSignalCollection(BaseModel):
    signals: List[ProcurementSignal] = Field(
        default_factory=list,
        description="List of procurement-related signals extracted from the cleaned markdown."
    )


logging.basicConfig(level=logging.INFO)


def test_crawl_graph_parallel(debth=0):
    target = CrawlTarget(
        name="Toronto Council",
        base_url="https://pub-calgary.escribemeetings.com/?MeetingViewID=4&fillWidth=1&Year=2026&Expanded=Intergovernmental%20Affairs%20Committee",
        debth=debth,
        allowed_prefixes=[],
        activ=True,
    )
    config = get_app_config()
    llm = LLMFactory.create_from_config(config.llm_configs[1])

    pydantic_extractor = ParallelPydanticExtractor(
        llm,
        ProcurementSignalCollection,
    )
    started_at = time.perf_counter()
    graph = CrawlGraph([target], pydantic_extractor)
    resources: list[WebResource] = asyncio.run(graph.run())
    semantic_extracts = graph.semantic_extracts
    tot: dict[int, dict] = {}
    index = 0
    for extract in semantic_extracts:
        tot[index] = {
            "result": extract.content.model_dump(),
            "url": extract.meta["url"],
            "page_number": extract.meta.get("page_number"),
        }
        index += 1
    save_path = rf"/Users/sinazabanfahm/projects/CRM/data/result_parallel.json"
    content_save_path = rf"/Users/sinazabanfahm/projects/CRM/data/contents_result_parallel.json"

    res = {}
    index = 0
    for resource in resources:
        res[index] = {
            "content": resource.content,
            "url": resource.url,
            "page_number": resource.meta_data.get("page_number"),
        }
        index += 1

    with open(content_save_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(tot, f, indent=2, ensure_ascii=False)
    ended_at = time.perf_counter()
    print(f"TIME USED FOR THE WHOLE PROCESS IS {ended_at - started_at}")
    assert resources is not None
    assert len(resources) > 0



test_crawl_graph_parallel(2)
