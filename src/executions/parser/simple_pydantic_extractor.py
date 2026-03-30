import logging
from pydantic import BaseModel
from typing import Type

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import WebResource
from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.executions.parser.llm_input_logging import log_llm_input
from src.prompts.parser import generic_extractor_prompt, generic_prompt_refiner


LOGGER = logging.getLogger(__name__)

class SimplePydanticExtractor(BaseExecution):
    input_spec = input_spec = (InputSpec(role = "web_resource", kind = InputKinds.WEBRESOURCE.value),
                               )

    def __init__(self, llm: BaseChatModel, base_model:BaseModel, chunk_size: int = 30000, chunk_overlap: int = 300,
                  name:str | None = None, id: str | None = None):
        super().__init__(name,id)
        self.llm = llm
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.base_model = base_model
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.chunk_size,
            chunk_overlap = self.chunk_overlap,
            separators= ["\n\n", "\n", " ", ""]
        )


    async def aexecute(self, state, run_id, inputs):
        model = self.base_model
        resource: WebResource = inputs["web_resource"].content
        text = resource.content
        result = await self.aextract(
            model,
            text,
            run_id=run_id,
            url=resource.url,
            page_number=resource.meta_data.get("page_number"),
        )
        out = Artifact[str](
            id = self.id,
            kind = InputKinds.MARKDOWN.value,
            name = self.name,
            content = result,
            meta={
                "url": resource.url,
                "page_number": resource.meta_data.get("page_number"),
            }
        )
        return [out]
    


    async def aextract(
        self,
        model: Type[BaseModel],
        text: str,
        *,
        run_id: str,
        url: str | None,
        page_number,
    ) -> BaseModel:
        chunks = self.splitter.split_text(text)
        if not chunks:
            raise ValueError(f"Cannot chunk {text[:min(len(text),20)]}")
        
        parser = PydanticOutputParser(pydantic_object = model)
        
        chain = generic_extractor_prompt | self.llm | parser
        format_instruction = parser.get_format_instructions()
        log_llm_input(
            LOGGER,
            stage="initial_extract",
            run_id=run_id,
            url=url,
            page_number=page_number,
            chunk=chunks[0],
            chunk_index=0,
            chunk_count=len(chunks),
        )
        current_obj = await chain.ainvoke(
            {
            "chunk" : chunks[0],
            "format_instructions" : format_instruction
            }
        )
        refine_chain = generic_prompt_refiner | self.llm | parser
        for chunk_index, chunk in enumerate(chunks[1:], start=1):
            try:
                log_llm_input(
                    LOGGER,
                    stage="refine_extract",
                    run_id=run_id,
                    url=url,
                    page_number=page_number,
                    chunk=chunk,
                    chunk_index=chunk_index,
                    chunk_count=len(chunks),
                    current_json=current_obj.model_dump_json(),
                )
                current_obj = await refine_chain.ainvoke(
                    {
                        "current_json": current_obj.model_dump_json(),
                        "chunk": chunk,
                        "format_instructions": format_instruction
                    }
                )
            except Exception as e:
                pass
        return current_obj
