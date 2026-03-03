from pydantic import (BaseModel, 
                      ConfigDict,
                      Field)



class LLMConfig(BaseModel):

    name: str = Field(..., description = "model_name")
    provider: str = Field(..., description= "Api provider")
    group_name: str = Field(..., description = "tag for grouping models")
    model_config = ConfigDict(extra = "allow")