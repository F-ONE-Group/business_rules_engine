from pydantic import Field
from pydantic.type_adapter import TypeAdapter
from typing import Annotated, Union
from .methods import *

TransformationMethod = Union[Set, Append, Format]

TransformationMethodAdapter = TypeAdapter(
    Annotated[TransformationMethod, Field(discriminator="transformation_method")]
)


def parse_transformation_method(method_info: dict) -> TransformationMethod:
    return TransformationMethodAdapter.validate_python(method_info)
