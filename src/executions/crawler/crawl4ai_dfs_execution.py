
import asyncio
import time

from crawl4ai import (CrawlerRunConfig, 
                      AsyncWebCrawler, 
                      CacheMode)
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter,
    ContentRelevanceFilter,
    SEOFilter
)
from crawl4ai.deep_crawling.scorers import (
    KeywordRelevanceScorer
)


from src.executions.base_execution import BaseExecution, InputSpec
from src.states.artifact import Artifact
