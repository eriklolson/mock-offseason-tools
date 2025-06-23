import os
import yaml
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Load credentials path from .env
load_dotenv()
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS", "auth/credentials.json")
TOKEN_PATH = ".token.json"

# Google Drive folder ID for '2025 TeamSheets'
FOLDER_ID = "1YUwfswiO_iVCb_cTQH6pde-miCzXWAd3"

# Required API scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

def authenticate():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
    return creds

def extract_team_name(filename: str) -> str:
    """Extract 'Charlotte Hornets' from 'Charlotte Hornets - Erik Olson'."""
    return filename.split(" - ")[0].strip()

def fetch_team_sheet_links(service):
    query = f"'{FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    team_links = {}
    for file in files:
        team_name = extract_team_name(file["name"])
        sheet_url = f"https://docs.google.com/spreadsheets/d/{file['id']}"
        team_links[team_name] = sheet_url

    return team_links

def write_yaml(data, path="config/team_sheets.yaml"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"✅ team_sheets.yaml written to {path} with {len(data)} teams.")

def main():
    creds = authenticate()
    drive_service = build("drive", "v3", credentials=creds)

    team_links = fetch_team_sheet_links(drive_service)
    write_yaml(team_links)

if __name__ == "__main__":
    main()
