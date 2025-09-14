import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile

class GoogleDriveHandler:
    def __init__(self, credentials_file, folder_id=None):
        """
        Initialize Google Drive handler
        
        Args:
            credentials_file (str): Path to Google service account credentials JSON file
            folder_id (str, optional): Specific folder ID to upload to
        """
        self.credentials_file = credentials_file
        self.folder_id = folder_id
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            raise Exception(f"Failed to authenticate with Google Drive: {str(e)}")
    
    def create_folder(self, folder_name, parent_folder_id=None):
        """
        Create a new folder in Google Drive
        
        Args:
            folder_name (str): Name of the folder to create
            parent_folder_id (str, optional): Parent folder ID
            
        Returns:
            str: ID of the created folder
        """
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            elif self.folder_id:
                folder_metadata['parents'] = [self.folder_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
        except Exception as e:
            raise Exception(f"Failed to create folder: {str(e)}")
    
    def upload_file(self, file_path, file_name, folder_id=None):
        """
        Upload a file to Google Drive
        
        Args:
            file_path (str): Local path to the file
            file_name (str): Name for the file in Google Drive
            folder_id (str, optional): Folder ID to upload to
            
        Returns:
            str: ID of the uploaded file
        """
        try:
            file_metadata = {
                'name': file_name
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            elif self.folder_id:
                file_metadata['parents'] = [self.folder_id]
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def upload_property_data(self, property_data, user_id):
        """
        Upload property data to Google Drive
        
        Args:
            property_data (dict): Property information
            user_id (str): Telegram user ID
            
        Returns:
            str: Folder ID where data was uploaded
        """
        try:
            # Create timestamp for folder name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"Property_{property_data.get('property_type', 'Unknown')}_{timestamp}"
            
            # Create folder
            folder_id = self.create_folder(folder_name)
            
            # Prepare data for upload
            data_to_upload = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'property_data': property_data
            }
            
            # Create temporary JSON file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(data_to_upload, temp_file, indent=2, ensure_ascii=False)
                temp_file_path = temp_file.name
            
            try:
                # Upload JSON file
                file_name = f"property_data_{timestamp}.json"
                self.upload_file(temp_file_path, file_name, folder_id)
                
                return folder_id
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            raise Exception(f"Failed to upload property data: {str(e)}")