from enum import Enum

class InputKinds(Enum):
    SCHEMA_REF = "schema_ref"
    TEXT = "text"
    MARKDOWN = "markdown"
    DATAFRAME = "dataframe"
    WEBRESOURCE = "web_resource"