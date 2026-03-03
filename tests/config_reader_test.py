from pathlib import Path
from src.config.app_config import get_app_config

def test_get_app_config():

    config = get_app_config()
    print(config)

test_get_app_config()