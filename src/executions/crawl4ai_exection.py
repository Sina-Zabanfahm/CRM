
import asyncio
from crawl4ai import (AsyncWebCrawler, 
                      BrowserConfig,
                      CrawlerRunConfig)

from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact
from src.executions.base_execution import (BaseExecution,
                                           InputSpec)

class Crawl4AIExecution(BaseExecution):

    input_spec = (InputSpec(role = "url", kind = "text"), )


    def execute(self, state: ExecutionState, run_id: str,
                inputs: dict[str, Artifact]) -> list[Artifact[str]]:
        
        url = inputs["url"]
        markdown = self._crawl_sync(url.content)

        out = Artifact[str](
            id = self.id,
            kind = "markdown",
            name = self.name,
            content = markdown
        )
        return [out]
    
    def _crawl_sync(self, url:str) -> str:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            raise RuntimeError(
                "Already in an event loop - use await"
            )
        return asyncio.run(self._crawl_async(url))
    
    async def _crawl_async(self, url: str) -> str:
        browser_cfg = BrowserConfig(headless = True)
        run_cfg = CrawlerRunConfig()

        async with AsyncWebCrawler(config= browser_cfg) as crawler:
            results = await crawler.arun(url, config = run_cfg)

        return results.markdown or ""