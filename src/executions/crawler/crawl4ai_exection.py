
from crawl4ai import (AsyncWebCrawler, 
                      BrowserConfig,
                      CrawlerRunConfig)
from crawl4ai.models import CrawlResult, CrawlResultContainer
from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact
from src.states.web_resources import WebResource
from src.executions.base_execution import (BaseExecution,
                                           InputSpec)

from src.executions.input_kinds import InputKinds

class Crawl4AIExecution(BaseExecution):

    input_spec = (InputSpec(role = "url", kind = InputKinds.TEXT.value), )

    
    async def aexecute(self, state: ExecutionState, run_id: str,
                inputs: dict[str, Artifact]) -> Artifact[WebResource]:
        
        url = inputs["url"]
        result: CrawlResult = await self._crawl_async(url.content)
        out = Artifact[str](
            id = self.id,
            kind = InputKinds.WEBRESOURCE.value,
            name = self.name,
            content = WebResource(
                url = result.url,
                content = result.markdown
            )
        )
        return out
    
    async def _crawl_async(self, url: str) -> CrawlResultContainer:
        browser_cfg = BrowserConfig(headless = True)
        run_cfg = CrawlerRunConfig()

        async with AsyncWebCrawler(config= browser_cfg) as crawler:
            results = await crawler.arun(url, config = run_cfg)

        return results
    
