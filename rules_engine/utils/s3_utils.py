import os
import boto3
from botocore.exceptions import NoCredentialsError, BotoCoreError
from urllib.parse import urlparse
from typing import Optional, Union
import backoff


def get_file_from_s3(bucket: str, file_name: str) -> Union[bytes, None]:
    """
    Retrieve an attachment from Amazon S3.

    Parameters:
        file_name (str): The name of the file to retrieve.
        bucket (str): The S3 bucket where the file is stored.

    Returns:
        File content in bytes if the file was retrieved successfully, False otherwise.
    """

    # Get the S3 client
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    # Try to retrieve the file from S3 for 10 seconds
    @backoff.on_exception(backoff.expo, BotoCoreError, max_time=10)
    def _get_object(bucket, file_name):
        response = s3.get_object(Bucket=bucket, Key=file_name)
        return response["Body"].read()

    try:
        return _get_object(bucket, file_name)

    except NoCredentialsError:
        print("No AWS credentials were found.")
    except Exception as e:
        print(f"An error occurred while retrieving the attachment: {e}")

    return None
