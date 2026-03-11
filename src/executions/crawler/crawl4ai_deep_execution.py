
import asyncio
import time

from crawl4ai import (CrawlerRunConfig, 
                      AsyncWebCrawler, 
                      )
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, BestFirstCrawlingStrategy
from crawl4ai.models import CrawlResult, CrawlResultContainer



from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds

from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource
class Crawl4aiDeepCrawl(BaseExecution):
    
    input_spec = (InputSpec(role = "url", kind = InputKinds.TEXT.value), )
    
    def __init__(self, name:str | None = None, id: str | None = None,
                 max_depth:int = 0, mean_delay: int = 0.3 ):
        super().__init__(name, id)
        self.max_depth = max_depth
        self.mean_delay = mean_delay
        self.crawler_config = CrawlerRunConfig(
            deep_crawl_strategy = BFSDeepCrawlStrategy(max_depth = self.max_depth),
            scraping_strategy =  LXMLWebScrapingStrategy(),
            verbose = True,
            mean_delay=mean_delay
        )

    async def basic_deep_crawl(self, url: str) -> CrawlResultContainer:
        config = self.crawler_config
        async with AsyncWebCrawler() as crawler:
            
            results = await crawler.arun(url = url,
                                         config = config)
            
        pages_by_depth = {} 
        for result in results:
            result: CrawlResult
            depth = (result.metadata or {}).get("depth", 0)
            if depth not in pages_by_depth:
                pages_by_depth[depth] = []
            
            pages_by_depth[depth].append(
                WebResource(
                    url = result.url,
                    content= result.markdown,
                )
            )
        return pages_by_depth
    
    async def aexecute( 
        self, 
        state: ExecutionState,
        run_id: str,
        inputs: dict[str, Artifact[str]]
    ) -> Artifact[dict[int, WebResource]]:
        url = inputs["url"]
        result = await self.basic_deep_crawl(url.content)
        out = Artifact[dict[int, WebResource]](
            id = self.id,
            name = self.name,
            content = result,
            kind=InputKinds.WEBRESOURCE
        )
        return out