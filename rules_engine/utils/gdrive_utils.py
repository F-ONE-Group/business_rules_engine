import io
from logging import root
import mimetypes
import os
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive"]
gdrive_folder = os.path.join(os.getcwd(), "gdrive")
os.makedirs(gdrive_folder, exist_ok=True)

token_file = os.path.join(gdrive_folder, "token.json")
credentials_file = os.path.join(gdrive_folder, "credentials.json")

logger = logging.getLogger("business_engine.gdrive_utils")
logger.setLevel(logging.DEBUG)


def get_credentials():
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds


def search_file(filename: str, mimetype: str):
    """Search file in drive location"""
    try:
        # create drive api client
        service = build("drive", "v3", credentials=get_credentials())
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = (
                service.files()
                .list(
                    q=f"mimeType='{mimetype}'",
                    spaces="drive",
                    fields="nextPageToken, " "files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                if file.get("name") == filename:
                    return file
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")
    return None


def download_file(file) -> str:
    """Downloads a file
    Args:
        file_id: ID of the file to download
    Returns : IO object with location.
    """
    filename = file.get("name")
    file_id = file.get("id")
    file_mimetype = file.get("mimeType")
    if file_mimetype is None:
        file_mimetype = "application/vnd.google-apps.spreadsheet"
    # create drive api client
    service = build("drive", "v3", credentials=get_credentials())
    # pylint: disable=maybe-no-member
    if file_mimetype == "application/vnd.google-apps.spreadsheet":
        request = service.files().export_media(
            fileId=file_id,
            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        logger.debug(f"Download {int(status.progress() * 100)}.")

    extension = mimetypes.guess_extension(file_mimetype)
    target = os.path.join(gdrive_folder, f"{filename}.{extension}")
    # with open(target, 'wb') as f:
    #     f.write(file.getvalue())

    return file.getvalue()
