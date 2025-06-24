#!/usr/bin/env python3

import os
import yaml
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ------------------------------------------------------------------------------
# Load environment variables from .env
# Used for GOOGLE_CREDENTIALS and GOOGLE_TOKEN_PATH
# ------------------------------------------------------------------------------

load_dotenv()

# ------------------------------------------------------------------------------
# Base directory: project root (assumes this file lives in joplin-sync/)
# ------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------------------
# Credential + token paths, pulled from .env or default fallback paths
# CREDENTIALS_PATH is the OAuth 2.0 client credentials downloaded from GCP
# TOKEN_PATH stores a generated refresh token to avoid repeated logins
# ------------------------------------------------------------------------------

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS", os.path.join(BASE_DIR, "auth/secrets/oauth/credentials.json"))
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", os.path.join(BASE_DIR, "auth/secrets/oauth/.token.json"))

# ------------------------------------------------------------------------------
# Output YAML path: will write config/teamsheets.yaml
# ------------------------------------------------------------------------------

CONFIG_PATH = os.getenv("teamsheets.yaml", os.path.join(BASE_DIR, "config", "teamsheets.yaml"))

# ------------------------------------------------------------------------------
# Google Drive folder ID of the shared folder: "2025 TeamSheets"
# All team sheets must live in this folder to be discovered
# ------------------------------------------------------------------------------

FOLDER_ID = "1YUwfswiO_iVCb_cTQH6pde-miCzXWAd3"

# ------------------------------------------------------------------------------
# Required API scopes:
# - Drive metadata to list files in the shared folder
# ------------------------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

# ------------------------------------------------------------------------------
# Authenticate with Google using OAuth2
# Reuses saved token from TOKEN_PATH if possible, otherwise triggers login
# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------
# Extract team name from file name pattern: 'Team Name - GM Name'
# ------------------------------------------------------------------------------

def extract_team_name(filename: str) -> str:
    """Extract 'Charlotte Hornets' from 'Charlotte Hornets - Erik Olson'."""
    return filename.split(" - ")[0].strip()

# ------------------------------------------------------------------------------
# Fetch all Google Sheets inside the shared 2025 TeamSheets folder
# Return a dict mapping team name → Google Sheets URL
# ------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------
# Write team_links dictionary to YAML file at CONFIG_PATH
# ------------------------------------------------------------------------------

def write_yaml(data, path=CONFIG_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"✅ teamsheets.yaml written to {path} with {len(data)} teams.")

# ------------------------------------------------------------------------------
# Main logic: authenticate, fetch sheet links, write YAML config
# ------------------------------------------------------------------------------

def main():
    creds = authenticate()
    drive_service = build("drive", "v3", credentials=creds)

    team_links = fetch_team_sheet_links(drive_service)
    write_yaml(team_links)

if __name__ == "__main__":
    main()
