import os
from pathlib import Path

from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.environment_variables.constants import APP_CONFIG_PATH
from src.config.llm_config import LLMConfig
from config_reader import load_dict


load_dotenv()


class AppConfig(BaseModel):

    llm_configs: list[LLMConfig] = Field(
        default_factory= list, description = "Available LLMs"
    )

    def resolve_config_path(cls, config_path: str | None) -> Path:
        if config_path is not None:
            path = Path(config_path)
            if not Path.exists(path):
                raise FileNotFoundError(f"File Not Exist {path}")
            return path
        
        if path_str :=os.getenv(APP_CONFIG_PATH):
            path = Path(path_str)
            if not Path.exists(path):
                raise FileNotFoundError("""
                    Config file resolved from environment file 
                    does not exit.
                    """)
            return path 
        
        raise FileNotFoundError(
            "Config file is not provided",
            f"environment variables does not include {APP_CONFIG_PATH}"
        )
    
    @classmethod
    def read_from_file(cls, config_path: str | None) -> 'AppConfig':
        resolved_path = cls.resolve_config_path(config_path)
        raw_dict = load_dict(resolved_path)
        result = cls.model_validate(raw_dict)
        return result
    

_app_config: AppConfig | None = None

def get_app_config() -> AppConfig:
    global _app_config 
    if _app_config is None:
        _app_config = AppConfig.read_from_file()
    return _app_config

def reset_app_config() -> None:
    global _app_config 
    _app_config = None
