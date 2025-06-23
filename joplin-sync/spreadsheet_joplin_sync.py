#!/usr/bin/env python3

import os
import yaml
import requests
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ------------------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------------------

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
TEAM_SHEETS_PATH = os.path.join(BASE_DIR, "config", "team_sheets.yaml")

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", BASE_DIR / "auth/secrets/oauth/credentials.json")
GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", BASE_DIR / "auth/secrets/oauth/.token.json")

# Joplin Web Clipper setup
JOPLIN_API = os.getenv("JOPLIN_API", "http://127.0.0.1:41184")
JOPLIN_NOTEBOOK_ID = "67e975d394dd43e9bde397740bbe821b"

# ------------------------------------------------------------------------------
# OAuth Scopes
# ------------------------------------------------------------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

# ------------------------------------------------------------------------------
# Cell background color → status marker mapping
# ------------------------------------------------------------------------------

COLOR_MARKER_MAP = {
    "red": "CH",     # Cap Hold
    "green": "PO",   # Player Option
    "blue": "TO",    # Team Option
    "orange": "10D", # 10 Day
    "grey": "NG",    # Non-Guaranteed
}

# ------------------------------------------------------------------------------
# Google Authentication
# ------------------------------------------------------------------------------

def authenticate():
    creds = None
    if os.path.exists(GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
    return creds

# ------------------------------------------------------------------------------
# Load team sheet URLs from YAML
# ------------------------------------------------------------------------------

def load_team_sheets():
    with open(TEAM_SHEETS_PATH, "r") as f:
        return yaml.safe_load(f)

# ------------------------------------------------------------------------------
# Convert normalized RGB (0–1) to simplified color labels
# ------------------------------------------------------------------------------

def rgb_to_label(color_dict):
    if not color_dict:
        return None

    r = int(color_dict.get("red", 0) * 255)
    g = int(color_dict.get("green", 0) * 255)
    b = int(color_dict.get("blue", 0) * 255)

    if r > 200 and g < 100 and b < 100:
        return "red"
    elif g > 200 and r < 100 and b < 100:
        return "green"
    elif b > 200 and r < 100 and g < 100:
        return "blue"
    elif r > 200 and g > 100:
        return "orange"
    elif r > 100 and g > 100 and b > 100:
        return "grey"
    else:
        return None

# ------------------------------------------------------------------------------
# Get sheet data with formatting info
# ------------------------------------------------------------------------------

def get_sheet_data(service, sheet_id):
    result = service.spreadsheets().get(
        spreadsheetId=sheet_id,
        includeGridData=True,
        ranges="Roster",
        fields="sheets.data.rowData.values(effectiveValue,effectiveFormat.backgroundColor)"
    ).execute()
    return result["sheets"][0]["data"][0]["rowData"]

# ------------------------------------------------------------------------------
# Parse sheet rows → Markdown table
# ------------------------------------------------------------------------------

def parse_to_markdown(row_data):
    table = []
    header_row = []
    for i, row in enumerate(row_data):
        values = row.get("values", [])
        row_cells = []
        for cell in values:
            val = cell.get("effectiveValue", {})
            number = val.get("numberValue")
            string = val.get("stringValue")

            bg = cell.get("effectiveFormat", {}).get("backgroundColor", {})
            color = rgb_to_label(bg)
            marker = COLOR_MARKER_MAP.get(color)

            if number is not None:
                salary = f"${int(number):,}"
                cell_str = f"{marker} {salary}" if marker else salary
            elif string is not None:
                cell_str = string
            else:
                cell_str = ""

            row_cells.append(cell_str)

        if i == 0:
            header_row = row_cells
        else:
            table.append(row_cells)

    lines = []
    lines.append("| " + " | ".join(header_row) + " |")
    lines.append("|" + "|".join("---" for _ in header_row) + "|")
    for row in table:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)

# ------------------------------------------------------------------------------
# Push Markdown content to Joplin
# ------------------------------------------------------------------------------

def sync_to_joplin(title, markdown):
    # Check if note exists
    res = requests.get(f"{JOPLIN_API}/notes", params={
        "query": title,
        "type": "note",
        "notebook_id": JOPLIN_NOTEBOOK_ID
    })
    data = res.json().get("items", [])
    if data:
        note_id = data[0]["id"]
        requests.put(f"{JOPLIN_API}/notes/{note_id}", json={
            "title": title,
            "body": markdown
        })
    else:
        requests.post(f"{JOPLIN_API}/notes", json={
            "title": title,
            "parent_id": JOPLIN_NOTEBOOK_ID,
            "body": markdown
        })
    print(f"✅ Synced Joplin note for {title}")

# ------------------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------------------

def main():
    creds = authenticate()
    service = build("sheets", "v4", credentials=creds)
    teams = load_team_sheets()

    for team_name, sheet_url in teams.items():
        print(f"📥 Fetching: {team_name}")
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        row_data = get_sheet_data(service, sheet_id)
        md = parse_to_markdown(row_data)
        sync_to_joplin(team_name, md)

if __name__ == "__main__":
    main()
