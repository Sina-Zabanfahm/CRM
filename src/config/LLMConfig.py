from pydantic import (BaseModel, 
                      ConfigDict,
                      Field)



class LLMConfig(BaseModel):

    name: str = Field(..., description = "model_name")
    model_config = ConfigDict(extra = "allow")