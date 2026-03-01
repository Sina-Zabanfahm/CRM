from abc import ABC, abstractmethod
from dataclasses import dataclass
@dataclass
class ConfigType(ABC):
    input_folder_path: str
    output_folder_path: str