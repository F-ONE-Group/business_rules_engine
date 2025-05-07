from pydantic import BaseModel
from typing import Any, Dict, Literal


TransformationMethodsType = Literal["set", "append", "format"]


class TransfBaseMethod(BaseModel):
    transformation_method: TransformationMethodsType
    variable: str
    target_value: Any

    def apply(self, process_variables: Dict) -> Any:
        raise NotImplementedError
