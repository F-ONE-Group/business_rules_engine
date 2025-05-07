from pydantic import Field
from pydantic.type_adapter import TypeAdapter
from typing import Annotated, Union
from .methods import *

ComparisonMethod = Union[
    IsEmpty,
    LessThan,
    LessThanOrEqual,
    GreaterThan,
    GreaterThanOrEqual,
    EqualTo,
    NotEqualTo,
    StartsWith,
    EndsWith,
    ContainsString,
    MatchPatterns,
    Within,
    NotIn,
]

# Create the adapter once
ComparisonMethodAdapter = TypeAdapter(
    Annotated[ComparisonMethod, Field(discriminator="comparison_method")]
)


def parse_comparison_method(method_info: dict) -> ComparisonMethod:
    return ComparisonMethodAdapter.validate_python(method_info)
