import asyncio

from src.executions.graphs.crawl_graph import CrawlGraph
from src.states.web_resources import CrawlTarget, WebResource

import logging

logging.basicConfig(level=logging.INFO)
def test_crawl_graph():
    target = CrawlTarget(
        name="Calgary Council",
        base_url="https://www.calgary.ca/council/",
        debth=1,
        allowed_prefixes=[],
        activ=True,
    )

    graph = CrawlGraph([target])
    resources: list[WebResource] = asyncio.run(graph.run())

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

    assert all(
        resource.error is None or isinstance(resource.error, str)
        for resource in resources
    )

test_crawl_graph()