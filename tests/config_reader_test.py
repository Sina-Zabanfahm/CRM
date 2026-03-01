from pathlib import Path
from src.config.config_type import ConfigType
from src.config.config_reader import ConfigReader
from tests.constants import FILLER
def test_config_loads_correctly_json():
    print(FILLER)
    print("Testing Config Loader Json")
    config_path  = Path("./configs/config.json")
    config: ConfigType = ConfigReader(config_path).read()
    assert config.input_folder_path != ""
    assert config.output_folder_path != ""
    print("DONE")
    print(FILLER)

def test_config_loads_correctly_yaml():
    print(FILLER)
    print("Testing Config Loader print")
    config_path  = Path("./configs/config.yaml")
    config: ConfigType = ConfigReader(config_path).read()
    assert config.input_folder_path != ""
    assert config.output_folder_path != ""
    print("DONE")
    print(FILLER)
    

test_config_loads_correctly_json()
test_config_loads_correctly_yaml()