import pytest
from rules_engine.external_source import (
    AirTableExternalSource,
    GDriveExternalSource,
    S3ExternalSource,
    ExcelExternalSource,
    CsvExternalSource,
)
from rules_engine.get_external_source import get_ext_source


@pytest.mark.parametrize(
    "input_source, expected_model",
    [
        (
            {
                "source": "airtable",
                "base_id": "test_base",
                "table": "test_table",
                "airtable_token": "token",
            },
            AirTableExternalSource,
        ),
        (
            {
                "source": "gdrive",
                "file_name": "test_file.xlsx",
                "mimetype": "test",
            },
            GDriveExternalSource,
        ),
        (
            {"source": "s3", "bucket": "test_bucket", "file_name": "test_file.xlsx"},
            S3ExternalSource,
        ),
        (
            {"source": "excel", "file_name": "test_file.xlsx"},
            ExcelExternalSource,
        ),
        (
            {"source": "csv", "file_name": "test_file.csv"},
            CsvExternalSource,
        ),
    ],
)
def test_class_assignment(input_source, expected_model):
    assert isinstance(get_ext_source(input_source), expected_model)
