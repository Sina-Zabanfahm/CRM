import os
import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from src.config.app_config import get_app_config
from src.config.llm_config import LLMConfig
from src.models.provider_types import OPENROUTER
from src.environment_variables.constants import (OPEN_ROUTER_API_KEY,
                                                 OPEN_ROUTER_BASE_URL)


logger = logging.getLogger(__name__)


class LLMFactory:
    @classmethod
    def create_from_config(cls, llm_config: LLMConfig) -> BaseChatModel:
        if llm_config.provider == OPENROUTER:
<<<<<<< HEAD
            return cls.create_from_config_or(llm_config)
=======
            return cls.create_openrouter(llm_config)
>>>>>>> 2ff330d (llm_factory, openrouater implementation)
    
    @classmethod
    def create_openrouter(cls, llm_config: LLMConfig) -> BaseChatModel:
        api_key = llm_config.api_key
        if llm_config.api_key is None:
            api_key = os.getenv(OPEN_ROUTER_API_KEY)
        
        base_url = llm_config.base_url
        if llm_config.base_url is None:
            base_url = os.getenv(OPEN_ROUTER_BASE_URL)

        return ChatOpenAI(
            model_name = llm_config.name,
            base_url= base_url,
            api_key= api_key
        )