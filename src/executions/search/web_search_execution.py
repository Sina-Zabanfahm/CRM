from __future__ import annotations

import urllib.parse

from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.executions.crawler.crawl4ai_deep_execution import Crawl4aiDeepCrawl


class WebSearchExecution(BaseExecution):
    """
    Build a search URL from a query, then delegate crawling
    to Crawl4aiDeepCrawl.

    Returns a markdown artifact whose content is:
        dict[int, list[str]]
    mapping crawl depth -> markdown pages.
    """

    input_spec = (
        InputSpec(role="query", kind=InputKinds.TEXT.value),
    )

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        n_results: int = 5,
        max_depth: int = 1,
        search_engine: str = "duckduckgo",
    ):
        super().__init__(name, id)
        self.n_results = n_results
        self.max_depth = max_depth
        self.search_engine = search_engine

    async def aexecute(
    self,
    state: ExecutionState,
    run_id: str,
    inputs: dict[str, Artifact[str]],
    ) -> list[Artifact]:
        query = inputs["query"].content
        query_url = self._build_query_url(query)

        url_artifact = Artifact[str](
            id=f"{run_id}_query_url",
            kind=InputKinds.TEXT.value,
            name="url",
            content=query_url,
        )

        state.artifacts[run_id] = {
            "url": url_artifact
        }

        crawl_execution = Crawl4aiDeepCrawl(max_depth=self.max_depth)

        output = await crawl_execution.aexecute(
            state=state,
            run_id=run_id,
            inputs=state.artifacts[run_id],
        )

        crawled_content = output.content
        trimmed_content = self._trim_results(crawled_content)

        out = Artifact(
            id=self.id,
            kind=InputKinds.MARKDOWN.value,
            name=self.name or "search_results",
            content=trimmed_content,
        )
        return out

    def _build_query_url(self, query: str) -> str:
        encoded = urllib.parse.quote_plus(query)

        if self.search_engine == "duckduckgo":
            return f"https://duckduckgo.com/html/?q={encoded}"
        elif self.search_engine == "google":
            return f"https://www.google.com/search?q={encoded}"
        else:
            raise ValueError(f"Unsupported search engine: {self.search_engine}")

    def _trim_results(self, content: dict[int, list[str]]) -> dict[int, list[str]]:
        """
        Keep at most n_results pages total, preserving depth order.
        """
        trimmed: dict[int, list[str]] = {}
        count = 0

        for depth in sorted(content.keys()):
            if count >= self.n_results:
                break

            pages = content[depth]
            remaining = self.n_results - count
            selected = pages[:remaining]

            if selected:
                trimmed[depth] = selected
                count += len(selected)

        return trimmed