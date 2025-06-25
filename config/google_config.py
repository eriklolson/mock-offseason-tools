import os
from config.base import BASE_DIR  # Optional, if needed for path logic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==== Google Sheets Auth Config ====
CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CREDENTIALS",
    os.path.join(BASE_DIR, "auth/secrets/oauth/credentials.json")
)

TOKEN_PATH = os.getenv(
    "GOOGLE_TOKEN_PATH",
    os.path.join(BASE_DIR, "auth/secrets/oauth/.token.json")
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

# ==== Team Sheet Config ====
TEAM_SHEETS_CONFIG = os.getenv(
    "TEAM_SHEETS_CONFIG",
    os.path.join(BASE_DIR, "config", "teamsheets.yaml")
)