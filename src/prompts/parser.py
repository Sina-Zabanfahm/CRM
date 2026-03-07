
from langchain_core.prompts import ChatPromptTemplate

generic_extractor_prompt = ChatPromptTemplate.from_template(
    "Extract structured data from the text.\n\n"
    "{format_instructions}\n\n"
    "{chunk}"
)

generic_prompt_refiner = ChatPromptTemplate.from_messages(
    [
        ("system", "You refine an existing structured extraction using new evidence"),
        ("human"
         "Existing extranction (JSON):\n {current_json}\n\n"
         "Update it using only the text below: \n{format_instructions}"
         "NEW TEXT :\n {chunk}")
    ]
)