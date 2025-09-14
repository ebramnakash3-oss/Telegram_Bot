## Real Estate Data Entry Telegram Bot -> Google Drive

This bot collects real estate property data via Telegram and saves each submission in a new Google Drive folder as `data.json`.

### Collected fields
- Property type (Residential or Commercial)
- Address
- Area (e.g. 120 sqm)
- Google Maps location (URL)
- Owner name or phone number

### Requirements
- Python 3.10+
- A Telegram bot token
- Google Drive access via a Service Account (recommended) or OAuth client

### Setup
1. Copy `.env.example` to `.env` and fill in values.
2. For Google Drive credentials:
   - Service Account (recommended):
     - Create a Service Account in Google Cloud Console and download the JSON key file.
     - Put the file path in `GOOGLE_SERVICE_ACCOUNT_FILE`.
     - In Google Drive, create or identify a parent folder and share it with the service account email.
     - Put the parent folder ID in `GDRIVE_PARENT_FOLDER_ID`.
   - OAuth (alternative):
     - Provide `GOOGLE_OAUTH_CLIENT_SECRETS` and a `GOOGLE_TOKEN_FILE` already authorized for Drive.
3. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### Run
```bash
python bot.py
```

### Notes
- Each submission creates a folder named like `Residential - 123 Main St` under the configured parent folder and uploads `data.json` with the entered fields.
- If using a service account, ensure the Drive folder is shared with the service account email, otherwise folder creation will fail.