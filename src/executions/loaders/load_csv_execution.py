import pandas as pd

from src.states.artifact import Artifact
from src.executions.base_execution import BaseExecution, InputSpec
from src.executions.input_kinds import InputKinds


class LoadCSVExecution(BaseExecution):

    input_spec = (
        InputSpec(role="path", kind=InputKinds.TEXT.value),
    )

    def execute(self, state, run_id, inputs):

        path = inputs["path"].content
        df = pd.read_csv(path)

        artifact = Artifact(
            id=self.id,
            kind= InputKinds.DATAFRAME.value,
            name="csv_data",
            content= df
        )

        return [artifact]