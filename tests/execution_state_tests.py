
import pandas as pd 

from src.states.execution_state import ExecutionState
from src.states.artifact import Artifact
from src.states.error_log import ErrorLog

def all_null_execution_states():
    state = ExecutionState(
        None, None, None
    )
    assert state is not None
    print("DONE")

def check_generic_type_artifact():
    df = pd.DataFrame()
    artifact = Artifact[pd.DataFrame](
        "1", "TEST", "artifact", df
    )
    assert artifact is not None
    print("DONE")


all_null_execution_states()
check_generic_type_artifact()
