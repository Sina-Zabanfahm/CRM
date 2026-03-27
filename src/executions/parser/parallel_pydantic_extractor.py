from __future__ import annotations

import asyncio
import json
import logging
from typing import Type

from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.states.artifact import Artifact
from src.states.web_resources import WebResource
from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.prompts.parser import generic_extractor_prompt, generic_prompt_refiner

LOGGER = logging.getLogger(__name__)


class ParallelPydanticExtractor(BaseExecution):
    input_spec = (
        InputSpec(role="web_resource", kind=InputKinds.WEBRESOURCE.value),
    )

    def __init__(
        self,
        llm: BaseChatModel,
        base_model: Type[BaseModel],
        chunk_size: int = 8000,
        chunk_overlap: int = 200,
        max_concurrency: int = 5,
        name: str | None = None,
        id: str | None = None,
    ):
        super().__init__(name, id)
        self.llm = llm
        self.base_model = base_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_concurrency = max_concurrency
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    async def aexecute(self, state, run_id, inputs):
        resource: WebResource = inputs["web_resource"].content
        text = resource.content

        result = await self.aextract(self.base_model, text)

        out = Artifact[str](
            id=self.id,
            kind=InputKinds.MARKDOWN.value,
            name=self.name,
            content=result,
            meta={
                "url": resource.url,
                "page_number": resource.meta_data.get("page_number"),
            },
        )
        return [out]

    async def aextract(self, model: Type[BaseModel], text: str) -> BaseModel:
        chunks = self.splitter.split_text(text)
        if not chunks:
            raise ValueError(f"Cannot chunk text: {text[: min(len(text), 20)]}")

        partial_results = await self._extract_chunks_parallel(model, chunks)
        merged_result = await self._merge_partial_results(model, partial_results)
        return merged_result

    async def _extract_chunks_parallel(
        self,
        model: Type[BaseModel],
        chunks: list[str],
    ) -> list[BaseModel]:
        parser = PydanticOutputParser(pydantic_object=model)
        format_instructions = parser.get_format_instructions()
        chain = generic_extractor_prompt | self.llm | parser

        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def extract_one(idx: int, chunk: str) -> BaseModel | None:
            async with semaphore:
                try:
                    return await chain.ainvoke(
                        {
                            "chunk": chunk,
                            "format_instructions": format_instructions,
                        }
                    )
                except Exception as e:
                    LOGGER.exception("Chunk extraction failed for chunk %s: %s", idx, e)
                    return None

        tasks = [extract_one(i, chunk) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)

        partial_results = [r for r in results if r is not None]
        if not partial_results:
            raise ValueError("All chunk extraction calls failed.")

        return partial_results

    async def _merge_partial_results(
        self,
        model: Type[BaseModel],
        partial_results: list[BaseModel],
    ) -> BaseModel:
        if len(partial_results) == 1:
            return partial_results[0]

        parser = PydanticOutputParser(pydantic_object=model)
        format_instructions = parser.get_format_instructions()

        partial_json_list = [
            result.model_dump(mode="json") for result in partial_results
        ]

        merge_prompt = generic_prompt_refiner

        merge_chain = merge_prompt | self.llm | parser

        merged = await merge_chain.ainvoke(
            {
                "current_json": json.dumps(partial_json_list, ensure_ascii=False),
                "chunk": (
                    "Merge the list of extracted partial JSON objects into a single "
                    "final JSON object. Deduplicate repeated information, preserve "
                    "all valid fields, and return one schema-compliant result."
                ),
                "format_instructions": format_instructions,
            }
        )
        return merged
