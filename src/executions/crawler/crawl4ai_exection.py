
import asyncio
from crawl4ai import (AsyncWebCrawler, 
                      BrowserConfig,
                      CrawlerRunConfig)

from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact
from src.executions.base_execution import (BaseExecution,
                                           InputSpec)
from src.executions.input_kinds import InputKinds
class Crawl4AIExecution(BaseExecution):

    input_spec = (InputSpec(role = "url", kind = InputKinds.TEXT.value), )


    async def aexecute(self, state: ExecutionState, run_id: str,
                inputs: dict[str, Artifact]) -> list[Artifact[str]]:
        
        url = inputs["url"]
        markdown = await self._crawl_async(url.content)

        out = Artifact[str](
            id = self.id,
            kind = "markdown",
            name = self.name,
            content = markdown
        )
        return [out]
    
    async def _crawl_async(self, url: str) -> str:
        browser_cfg = BrowserConfig(headless = True)
        run_cfg = CrawlerRunConfig()

        async with AsyncWebCrawler(config= browser_cfg) as crawler:
            results = await crawler.arun(url, config = run_cfg)

        return results.markdown or ""
    
