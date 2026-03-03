from pathlib import Path
import os

from src.environment_variables.constants import (
                                BASE_DIR)   
class PathManager:

    def __init__(self, base_dir: str | Path | None):
        self.base_dir = base_dir

    @property
    def base_dir(self) -> Path:
        if self.base_dir is not None:
            return self.base_dir
        
        if base_dir := os.getenv(BASE_DIR):
            return base_dir
        
        raise FileNotFoundError("Cannot resolve Base Dir file")
    