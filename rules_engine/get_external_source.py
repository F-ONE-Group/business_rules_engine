from typing import Annotated, Union
from pydantic import Field
from pydantic.type_adapter import TypeAdapter

from .external_source import (
    AirTableExternalSource,
    GDriveExternalSource,
    S3ExternalSource,
    ExcelExternalSource,
    CsvExternalSource,
)

ExternalSourceTypes = Union[
    AirTableExternalSource,
    GDriveExternalSource,
    S3ExternalSource,
    ExcelExternalSource,
    CsvExternalSource,
]

ExtSourceAdapter = TypeAdapter(
    Annotated[ExternalSourceTypes, Field(discriminator="source")]
)


def get_ext_source(ext_data_info: dict) -> ExternalSourceTypes:
    return ExtSourceAdapter.validate_python(ext_data_info)
