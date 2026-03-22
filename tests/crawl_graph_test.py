import asyncio

from typing import Optional, Literal, List
from pydantic import BaseModel, Field

from src.config.app_config import get_app_config
from src.models.llm_factory import LLMFactory
from src.executions.parser.simple_pydantic_extractor import SimplePydanticExtractor
from src.executions.graphs.crawl_graph import CrawlGraph
from src.states.web_resources import CrawlTarget, WebResource
import logging
import json
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
    description: str = Field(..., description="Description of the offering")
    issuer: Optional[str] = Field(None, description="Organization, municipality, or agency issuing the notice.")
    due_date: Optional[str] = Field(None, description="Submission or closing date if present.")
    posting_date: Optional[str] = Field(None, description="Posting date if present.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this extraction.")
    budget: Optional[float] =  Field(0, description="Allocated budget")


class ProcurementSignalCollection(BaseModel):
    signals: List[ProcurementSignal] = Field(
        default_factory=list,
        description="List of procurement-related signals extracted from the cleaned markdown."
    )
logging.basicConfig(level=logging.INFO)
def test_crawl_graph(debth = 0):
    target = CrawlTarget(
        name="Calgary Council",
        base_url="https://pub-calgary.escribemeetings.com/Meeting.aspx?Id=a289cb13-b0c5-40df-8208-baea2ede6873&Agenda=Agenda&lang=English",
        debth=debth,
        allowed_prefixes=[],
        activ=True,
    )
    config = get_app_config()
    llm = LLMFactory.create_from_config(config.llm_configs[1])

    pydantic_extractor = SimplePydanticExtractor(llm, ProcurementSignalCollection)

    graph = CrawlGraph([target],pydantic_extractor)
    resources: list[WebResource] = asyncio.run(graph.run())
    semantic_extracts = graph.semantic_extracts
    tot: dict[int,dict] = {}
    index = 0
    for extract in semantic_extracts:
        tot[index] = {
            "result":extract.content.model_dump(),
            "url": extract.meta["url"]
            }
        index+=1
    save_path = rf"/Users/sinazabanfahm/projects/CRM/data/result.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(tot, f, indent=2, ensure_ascii=False)

    assert resources is not None
    assert len(resources) > 0

    assert any(
        resource.url.startswith("https://www.calgary.ca/council/")
        or (
            resource.final_url is not None
            and resource.final_url.startswith("https://www.calgary.ca/council/")
        )
        for resource in resources
    )

    

test_crawl_graph(0)