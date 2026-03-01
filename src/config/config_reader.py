# src/config/config_reader.py
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any
import json
import yaml

from src.config.config_type import ConfigType  
class ConfigReader:

    def __init__(self, path: Path):
        self.path = path
        self.config_dict: Dict[str, Any] = {}
    
    def read(self) -> Dict[str, Any]:
        extension = self.path.suffix
        if extension == ".json":
            self.config_dict =  self.read_json(self.path)
        elif extension in (".yaml", ".yml"):
            self.config_dict =  self.read_yaml(self.path)
        else:
            raise ValueError(f"Unsupported config file extension: {extension}")

        return self.to_config_type()
    @staticmethod
    def read_yaml(path: str) -> Dict[str, Any]:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return data

    @staticmethod
    def read_json(path: str) -> Dict[str, Any]:
        """Read JSON file and return as dictionary"""
        with open(path, "r") as f:
            data = json.load(f)
        return data

    def to_config_type(self) -> ConfigType:
        if not self.config_dict:
            self.config_dict = self.read()
        return ConfigType(**self.config_dict)