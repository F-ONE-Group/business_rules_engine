import io
import os
from typing import Literal, Self

import pandas as pd
import requests
from pydantic import BaseModel, model_validator, field_validator


class ExternalSourceException(Exception):
    pass


def remove_trailing_spaces(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes trailing spaces from all string cells in the given DataFrame.

    Args:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with trailing spaces removed.
    """
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)


class ExternalSource(BaseModel):
    data: pd.DataFrame = pd.DataFrame()

    class Config:
        arbitrary_types_allowed = True

    def get_bytes(cls):
        """Get the excel binary of the dataframe hosting the data

        Returns:
            bytes: bytes of the excel
        """
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        if cls.data.empty:
            cls.get_data()
        cls.data.to_excel(writer, sheet_name="Sheet1", index=False)
        writer.save()
        output.seek(0)
        return output

    def get_data(cls):
        pass


class AirTableExternalSource(ExternalSource):
    source: Literal["airtable"]
    airtable_token: str
    base_id: str
    table: str

    def get_data(cls) -> pd.DataFrame:
        data = []
        still_data = True
        offset = 0
        while still_data:
            url = f"https://api.airtable.com/v0/{cls.base_id}/{cls.table}"
            url_schema = f"https://api.airtable.com/v0/meta/bases/{cls.base_id}/tables"
            header = {"Authorization": f"Bearer {cls.airtable_token}"}
            res = requests.get(url, headers=header, data={}, params={"offset": offset})
            if res.status_code == 200:
                table = res.json()["records"]
                for x in table:
                    x.update(x.get("fields"))
                    x.pop("fields")
                    data.append(x)
                if res.json().get("offset", ""):
                    offset = res.json()["offset"]
                else:
                    still_data = False
            else:
                raise ExternalSourceException(res.text)
        df = pd.DataFrame(data)
        # get schema of the table
        url_schema = url_schema.format(base_id=cls.base_id)
        res = requests.get(url_schema, headers=header, data={})
        # get the name of the column of type date
        date_columns = []
        if res.status_code == 200:
            tables_schema = res.json()["tables"]
            for table in tables_schema:
                if table["name"] == cls.table:
                    for field in table["fields"]:
                        if field["type"] == "date":
                            date_columns.append(field["name"])
                    break
        for date_column in date_columns:
            df[date_column] = pd.to_datetime(df[date_column], format="%Y-%m-%d")

        cls.data = df
        return remove_trailing_spaces(cls.data)


class GDriveExternalSource(ExternalSource):
    source: Literal["gdrive"]
    file_name: str
    mimetype: str = "application/vnd.google-apps.spreadsheet"

    @field_validator("file_name")
    def check_extension(cls, value: str):
        if not value.endswith((".xlsx", ".csv")):
            raise ValueError(
                "The external source should be either a .xlsx or .csv file"
            )
        return value

    def get_data(cls) -> pd.DataFrame:
        from utils import gdrive_utils

        file = gdrive_utils.search_file(cls.file_name, cls.mimetype)
        if file is not None:
            file_b = gdrive_utils.download_file(file)
            if cls.file_name.endswith(".csv"):
                cls.data = pd.read_csv(file_b)
            else:
                cls.data = pd.read_excel(file_b)
            return remove_trailing_spaces(cls.data)
        else:
            raise ExternalSourceException("The external source cannot be found")


class S3ExternalSource(ExternalSource):
    source: Literal["s3"]
    bucket: str
    file_name: str

    @field_validator("file_name", mode="before")
    def check_extension(cls, value: str):
        if not value.endswith((".xlsx", ".csv")):
            raise ExternalSourceException(
                "The external source should be either a .xlsx or .csv file"
            )
        return value

    @model_validator(mode="after")
    def check_if_aws_keys_are_available(self: Self) -> Self:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if aws_access_key_id is None or aws_secret_access_key is None:
            raise ExternalSourceException(
                "Please provide valid AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
            )
        return self

    def get_data(cls) -> pd.DataFrame:
        from utils import s3_utils

        file_b = s3_utils.get_file_from_s3(cls.bucket, cls.file_name)
        if file_b is not None:
            if cls.file_name.endswith(".csv"):
                cls.data = pd.read_csv(
                    io.BytesIO(file_b),
                )
            else:
                cls.data = pd.read_excel(io.BytesIO(file_b))
            return remove_trailing_spaces(cls.data)
        else:
            raise ExternalSourceException("The external source cannot be found")


class ExcelExternalSource(ExternalSource):
    source: Literal["excel"]
    file_name: str

    @field_validator("file_name")
    def check_extension(cls, value: str):
        if not value.lower().endswith((".xlsx")):
            raise ExternalSourceException(
                "The external source should be either a .xlsx or .csv file"
            )
        return value

    def get_data(cls) -> pd.DataFrame:
        if os.path.exists(cls.file_name):
            cls.data = pd.read_excel(cls.file_name)
            return remove_trailing_spaces(cls.data)
        else:
            raise FileExistsError(cls.file_name)


class CsvExternalSource(ExternalSource):
    source: Literal["csv"]
    file_name: str

    @field_validator("file_name")
    def check_extension(cls, value: str):
        if not value.lower().endswith((".csv")):
            raise ExternalSourceException(
                "The external source should be either a .xlsx or .csv file"
            )
        return value

    def get_data(cls) -> pd.DataFrame:
        if os.path.exists(cls.file_name):
            cls.data = pd.read_csv(cls.file_name)
            return remove_trailing_spaces(cls.data)
        else:
            raise FileExistsError(cls.file_name)
