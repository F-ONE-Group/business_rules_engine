import numpy as np
from pydantic import BaseModel, field_validator
from typing import List, Literal, Any, Union

ComparisonMethodTypes = Literal[
    "is_empty",
    "less_than",
    "less_than_or_equal_to",
    "greater_than",
    "greater_than_or_equal_to",
    "equal_to",
    "not_equal_to",
    "starts_with",
    "ends_with",
    "contains_string",
    "matches_pattern",
    "within",
    "not_in",
]


class ComparisonBaseMethod(BaseModel):
    comparison_method: ComparisonMethodTypes
    variable: Any
    comparison_variables: Union[Any, List[Any]]

    @field_validator("variable", "comparison_variables", mode="before")
    def convert_to_datetime(cls, value):
        if isinstance(value, np.datetime64):
            # this is an external variable of type np.datetime64
            from datetime import datetime

            value = datetime.fromtimestamp(int(value) / 1e9)
        return value

    def evaluate(self) -> bool:
        raise NotImplementedError
