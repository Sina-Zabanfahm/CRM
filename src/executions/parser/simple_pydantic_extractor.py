
from pydantic import BaseModel
from typing import Type

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds
from src.prompts.parser import generic_extractor_prompt, generic_prompt_refiner

class SimplePydanticExtractor(BaseExecution):
    input_spec = input_spec = (InputSpec(role = "content", kind = InputKinds.TEXT.value),
                               )

    def __init__(self, llm: BaseChatModel, base_model:BaseModel, chunk_size: int = 3000, chunk_overlap: int = 300,
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
        text = inputs["content"].content
        result = await self.aextract(model, text)
        out = Artifact[str](
            id = self.id,
            kind = InputKinds.MARKDOWN.value,
            name = self.name,
            content = result
        )
        return out
    


    async def aextract(self, model: Type[BaseModel], text:str) -> BaseModel:
        chunks = self.splitter.split_text(text)
        if not chunks:
            raise ValueError(f"Cannot chunk {text[:min(len(text),20)]}")
        
        parser = PydanticOutputParser(pydantic_object = model)
        
        prompt = generic_extractor_prompt
        chain = generic_extractor_prompt | self.llm | parser

        current_obj = chain.invoke(
            {
            "chunk" : chunks[0],
            "format_instructions" : parser.get_format_instructions()
            }
        )

        refine_chain = generic_prompt_refiner | self.llm | parser
        for chunk in chunks[1:]:
            current_obj = await refine_chain.ainvoke(
                {
                    "current_json": current_obj.model_dump_json(),
                    "chunk": chunk,
                    "format_instructions": parser.get_format_instructions(),
                }
            )
        return current_obj