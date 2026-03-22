
from __future__ import annotations

import logging

from src.executions.crawler.crawl4ai_deep_execution import Crawl4aiDeepCrawl
from src.executions.fetch.fetch_execution import FetchExecution
from src.executions.fingerprint.finger_print_execution import FingerprintExecution
from src.executions.gating.llm_gate_execution import LlmGateExecution
from src.executions.input_kinds import InputKinds
from src.executions.normalize.normalize_execution import NormalizeExecution
from src.executions.parser.simple_pydantic_extractor import SimplePydanticExtractor
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import CrawlTarget, WebResource

logger = logging.getLogger(__name__)


class CrawlGraph:
    def __init__(
        self,
        targets: list[CrawlTarget],
        pydantic_extractor: SimplePydanticExtractor,
        *,
        mean_delay: float = 0.1,
        fetch_execution: FetchExecution | None = None,
        normalize_execution: NormalizeExecution | None = None,
        fingerprint_execution: FingerprintExecution | None = None,
        gate_execution: LlmGateExecution | None = None,
    ):
        self.targets = targets
        self.mean_delay = mean_delay
        self.fetch_execution = fetch_execution or FetchExecution()
        self.normalize_execution = normalize_execution or NormalizeExecution()
        self.fingerprint_execution = (
            fingerprint_execution or FingerprintExecution()
        )
        self.gate_execution = gate_execution or LlmGateExecution()
        self.pydantic_extractor = pydantic_extractor
        self.semantic_extracts: list = []
    async def run(self) -> list[WebResource]:
        state = ExecutionState()
        processed_resources: list[WebResource] = []
        logger.info("Starting crawl graph for %s targets.", len(self.targets))

        for target_index, target in enumerate(self.targets):
            if not target.activ:
                logger.info("Skipping inactive target %s (%s).", target_index, target.base_url)
                continue

            logger.info("Processing target %s: %s", target_index, target.base_url)
            crawled_resources = await self._crawl_target(state, target_index, target)
            logger.info(
                "Target %s produced %s allowed resources.",
                target_index,
                len(crawled_resources),
            )

            for resource_index, resource in enumerate(crawled_resources):
                processed_resource = await self._process_resource(
                    state,
                    target_index,
                    resource_index,
                    resource,
                )
                curr_content: WebResource = processed_resource
                run_id = f"target-{target_index}"
                if curr_content.should_pass_to_llm:
                    text_artifact = Artifact[WebResource](
                    id=f"target-{target_index}",
                    kind=InputKinds.WEBRESOURCE.value,
                    content=curr_content,
                    name="web_resource",
                    )
                    state.artifacts[run_id] = {
                        "web_resource": text_artifact
                    }
                    try:
                        self.semantic_extracts+= await self.pydantic_extractor.arun(state, run_id)
                    except Exception as e:
                        print(e)
                processed_resources.append(processed_resource)

        logger.info(
            "Crawl graph completed with %s processed resources.",
            len(processed_resources),
        )
        return processed_resources

    async def _crawl_target(
        self,
        state: ExecutionState,
        target_index: int,
        target: CrawlTarget,
    ) -> list[WebResource]:
        run_id = f"target-{target_index}"
        logger.info("Starting crawl for target %s with run_id=%s.", target_index, run_id)
        state.artifacts[run_id] = {
            "url": Artifact[str](
                id=run_id,
                kind=InputKinds.TEXT.value,
                name="url",
                content=target.base_url,
            )
        }

        execution = Crawl4aiDeepCrawl(
            max_depth=target.debth,
            mean_delay=self.mean_delay,
        )
        output = await execution.arun(state, run_id)

        resources: list[WebResource] = []
        for resource_list in output.content.values():
            for resource in resource_list:
                if self._is_allowed_resource(target, resource):
                    resources.append(resource)
        logger.info(
            "Finished crawl for target %s with %s allowed resources.",
            target_index,
            len(resources),
        )
        return resources

    async def _process_resource(
        self,
        state: ExecutionState,
        target_index: int,
        resource_index: int,
        resource: WebResource,
    ) -> WebResource:
        run_id = f"target-{target_index}-resource-{resource_index}"
        logger.info(
            "Processing resource %s for target %s: %s",
            resource_index,
            target_index,
            resource.target_url,
        )
        current_artifact = Artifact[WebResource](
            id=run_id,
            kind=InputKinds.WEBRESOURCE.value,
            name="web_resource",
            content=resource,
        )

        for execution in (
            self.fetch_execution,
            self.normalize_execution,
            self.fingerprint_execution,
            self.gate_execution,
        ):
            state.artifacts[run_id] = {"web_resource": current_artifact}
            logger.info(
                "Running %s for resource %s of target %s.",
                execution.name,
                resource_index,
                target_index,
            )
            current_artifact = await execution.arun(state, run_id)

        logger.info(
            "Finished resource %s for target %s. should_pass_to_llm=%s error=%s",
            resource_index,
            target_index,
            current_artifact.content.should_pass_to_llm,
            current_artifact.content.error,
        )
        return current_artifact.content

    @staticmethod
    def _is_allowed_resource(target: CrawlTarget, resource: WebResource) -> bool:
        if len(target.allowed_prefixes) == 0:
            return True

        return any(
            candidate_url.startswith(prefix)
            for prefix in target.allowed_prefixes
            for candidate_url in (resource.url, resource.target_url)
            if candidate_url is not None
        )
