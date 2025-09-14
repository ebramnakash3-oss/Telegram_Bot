import os
import json
from typing import Optional, Dict, Any

from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaInMemoryUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


class DriveClient:
    def __init__(self,
                 parent_folder_id: str,
                 service_account_file: Optional[str] = None,
                 oauth_client_secrets: Optional[str] = None,
                 oauth_token_file: Optional[str] = None) -> None:
        self.parent_folder_id = parent_folder_id
        self.service_account_file = service_account_file
        self.oauth_client_secrets = oauth_client_secrets
        self.oauth_token_file = oauth_token_file
        self._service = None

    def _get_service(self):
        if self._service is not None:
            return self._service

        creds = None
        if self.service_account_file and os.path.exists(self.service_account_file):
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=SCOPES
            )
        else:
            # Fallback to OAuth installed app flow using a token file if available
            if self.oauth_token_file and os.path.exists(self.oauth_token_file):
                creds = Credentials.from_authorized_user_file(self.oauth_token_file, SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
            else:
                raise RuntimeError(
                    "No valid Google credentials found. Provide service account file or OAuth token file."
                )

        self._service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return self._service

    def ensure_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        service = self._get_service()
        parent = parent_id or self.parent_folder_id

        # Try find existing folder with same name under parent
        query = (
            f"mimeType = 'application/vnd.google-apps.folder' and "
            f"name = '{name.replace("'", "\\'")}' and '{parent}' in parents and trashed = false"
        )
        results = service.files().list(q=query, spaces="drive", fields="files(id, name)").execute()
        files = results.get("files", [])
        if files:
            return files[0]["id"]

        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent],
        }
        folder = service.files().create(body=file_metadata, fields="id").execute()
        return folder["id"]

    def upload_json(self, name: str, data: Dict[str, Any], parent_id: Optional[str] = None) -> str:
        service = self._get_service()
        parent = parent_id or self.parent_folder_id

        media = MediaInMemoryUpload(
            json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            mimetype="application/json",
            resumable=False,
        )
        file_metadata = {"name": name, "parents": [parent]}
        try:
            created = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            return created["id"]
        except HttpError as e:
            raise RuntimeError(f"Failed to upload JSON to Drive: {e}")