# src/config/config_reader.py
from pathlib import Path
from typing import Dict, Any
import json
import yaml



def load_dict(path: Path) -> Dict[str, Any]:
    suffix = path.suffix
    if suffix == ".json":
        return load_json(path)
    if suffix == ".yaml":
        return load_yaml(path)
    
def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r") as f:
            data = json.load(f)
    return data