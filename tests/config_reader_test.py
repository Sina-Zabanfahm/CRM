from pathlib import Path
from src.config.app_config import get_app_config
from src.models.llm_factory import LLMFactory
def test_get_app_config():
    
    config = get_app_config()
    assert len(config.llm_configs) != 0

def test_llm_setup_openrouter():
    config = get_app_config()
    llm = LLMFactory.create_from_config(config.llm_configs[0])
    assert llm is not None

def test_llm_generation():
    config = get_app_config()
    llm = LLMFactory.create_from_config(config.llm_configs[0])
    res = llm.invoke("hello")
    assert not (res.content is  None) or (res.content != "")

test_get_app_config()
test_llm_setup_openrouter()
test_llm_generation()