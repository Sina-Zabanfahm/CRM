
from src.states.web_resources import WebResource, CrawlTarget
from src.executions.crawler.crawl4ai_deep_execution import Crawl4aiDeepCrawl
from src.executions.fetch.fetch_execution import FetchExecution
from src.executions.normalize.normalize_execution import NormalizeExecution
from src.executions.fingerprint.finger_print_execution import FingerprintExecution
from src.executions.parser.simple_pydantic_extractor import SimplePydanticExtractor
class CrawlGraph:

    def __init__(self, targets: list[CrawlTarget]):
        self.targets = targets