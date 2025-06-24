#!/usr/bin/env python3

import os
import requests
import yaml
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS", os.path.join(BASE_DIR, "auth/secrets/oauth/credentials.json"))
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", os.path.join(BASE_DIR, "auth/secrets/oauth/.token.json"))
TEAM_SHEETS_CONFIG = os.getenv("TEAM_SHEETS_CONFIG", os.path.join(BASE_DIR, "config", "team_sheets.yaml"))

JOPLIN_API = os.getenv("JOPLIN_API", "http://127.0.0.1:41184")
JOPLIN_TOKEN = os.getenv("JOPLIN_TOKEN")
JOPLIN_NOTEBOOK_ID = os.getenv("JOPLIN_NOTEBOOK_ID")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
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

def load_team_sheets():
    with open(TEAM_SHEETS_CONFIG, "r") as f:
        return yaml.safe_load(f)

def get_sheet_data(service, sheet_id):
    result = service.spreadsheets().get(
        spreadsheetId=sheet_id,
        ranges=["Roster!C8:D25", "Roster!Q6:Q10"],
        includeGridData=True,
        fields="sheets.data.rowData.values(effectiveValue,effectiveFormat.backgroundColor,formattedValue)"
    ).execute()
    return result["sheets"]

def get_status_marker(cell):
    if "effectiveFormat" not in cell:
        return ""
    color = cell["effectiveFormat"].get("backgroundColor", {})
    r, g, b = color.get("red", 1), color.get("green", 1), color.get("blue", 1)

    def rgb_match(r, g, b, target):
        return abs(r - target[0]) < 0.1 and abs(g - target[1]) < 0.1 and abs(b - target[2]) < 0.1

    if rgb_match(r, g, b, (1.0, 0.6, 0.6)):
        return "CH"
    elif rgb_match(r, g, b, (0.6, 0.8, 0.6)):
        return "PO"
    elif rgb_match(r, g, b, (0.6, 0.6, 0.8)):
        return "TO"
    elif rgb_match(r, g, b, (1.0, 0.8, 0.6)):
        return "10D"
    elif rgb_match(r, g, b, (0.85, 0.85, 0.85)):
        return "NG"
    else:
        return ""

def format_summary(rows):
    labels = [
        "Salary for Cap",
        "Cap Space",
        "Luxury Tax Space",
        "1st Apron Space",
        "2nd Apron Space"
    ]

    markdown = "### 🧾 Cap Sheet Summary\n\n"
    markdown += "| Category | Amount |\n|----------|--------|\n"

    for i, row in enumerate(rows):
        cells = row.get("values", [])
        amount = cells[0].get("formattedValue", "").strip() if cells else ""
        if not amount:
            val = cells[0].get("effectiveValue", {}) if cells else {}
            if "numberValue" in val:
                amount = f"${val['numberValue']:,.0f}"
        if amount:
            markdown += f"| {labels[i]} | {amount} |\n"

    return markdown

def format_markdown(rows):
    markdown = "### 👥 Player Salaries\n\n"
    markdown += "| Player | Salary |\n|--------|--------|\n"
    for row in rows:
        cells = row.get("values", [])
        if not cells:
            continue
        name = cells[0].get("effectiveValue", {}).get("stringValue") or cells[0].get("formattedValue", "")
        salary_str = ""
        if len(cells) > 1:
            salary_cell = cells[1]
            val = salary_cell.get("effectiveValue", {}).get("numberValue")
            salary_str = f"${val:,.0f}" if val is not None else salary_cell.get("formattedValue", "")
            marker = get_status_marker(salary_cell)
            if marker:
                salary_str = f"{marker} {salary_str}"
        if name:
            markdown += f"| {name} | {salary_str} |\n"
    return markdown

def check_joplin_api_available():
    try:
        res = requests.get(f"{JOPLIN_API}/ping", timeout=3)
        if res.status_code != 200:
            raise Exception(f"Unexpected response code: {res.status_code}")
    except Exception as e:
        print(f"❌ Joplin API is not available: {e}")
        exit(1)

def get_notebook_path(folder_id):
    path_parts = []
    current_id = folder_id
    while current_id:
        res = requests.get(f"{JOPLIN_API}/folders/{current_id}", params={"token": JOPLIN_TOKEN})
        if res.status_code != 200:
            break
        data = res.json()
        path_parts.insert(0, data.get("title", current_id))
        current_id = data.get("parent_id")
    return "/".join(path_parts)

def notebook_exists(notebook_id):
    res = requests.get(f"{JOPLIN_API}/folders/{notebook_id}", params={"token": JOPLIN_TOKEN})
    return res.status_code == 200

def sync_note_to_joplin(title, markdown):
    if not JOPLIN_NOTEBOOK_ID:
        print(f"❌ Cannot create note '{title}' – JOPLIN_NOTEBOOK_ID is missing.")
        return
    if not notebook_exists(JOPLIN_NOTEBOOK_ID):
        print(f"❌ Notebook with ID '{JOPLIN_NOTEBOOK_ID}' not found.")
        return

    res = requests.get(f"{JOPLIN_API}/folders/{JOPLIN_NOTEBOOK_ID}/notes", params={"token": JOPLIN_TOKEN})
    items = [note for note in res.json().get("items", []) if note["title"] == title]

    if items:
        note = items[0]
        note_id = note["id"]
        parent_id = note.get("parent_id", JOPLIN_NOTEBOOK_ID)
        notebook_path = get_notebook_path(parent_id)
        print(f"✏️  Updating existing note in {notebook_path}/{title}")
        print(f"    (Notebook ID: {parent_id}, Note ID: {note_id})")
        requests.put(
            f"{JOPLIN_API}/notes/{note_id}",
            params={"token": JOPLIN_TOKEN},
            json={"body": markdown}
        )
    else:
        res = requests.post(
            f"{JOPLIN_API}/notes",
            params={"token": JOPLIN_TOKEN},
            json={
                "title": title,
                "body": markdown,
                "parent_id": JOPLIN_NOTEBOOK_ID
            }
        )
        if res.status_code != 200:
            print(f"❌ Failed to create note '{title}': {res.status_code} {res.text}")
            return
        note_id = res.json().get("id")
        notebook_path = get_notebook_path(JOPLIN_NOTEBOOK_ID)
        print(f"🆕 Creating note in {notebook_path}/{title}")
        print(f"    (Notebook ID: {JOPLIN_NOTEBOOK_ID}, Note ID: {note_id})")

    note_url = f"joplin://x-callback-url/openNote?id={note_id}"
    print(f"✅ Synced Joplin note for {title} → {note_url}")

def main():
    check_joplin_api_available()

    if not JOPLIN_NOTEBOOK_ID:
        raise ValueError("❌ JOPLIN_NOTEBOOK_ID is not set. Please check your .env file.")
    if not notebook_exists(JOPLIN_NOTEBOOK_ID):
        raise ValueError(f"❌ Joplin notebook ID '{JOPLIN_NOTEBOOK_ID}' is invalid or inaccessible.")

    creds = authenticate()
    service = build("sheets", "v4", credentials=creds)

    teams = load_team_sheets()
    for team, url in teams.items():
        print(f"📥 Fetching: {team}")
        sheet_id = url.split("/d/")[1].split("/")[0]
        try:
            sheet_data = get_sheet_data(service, sheet_id)

            row_data_players = []
            row_data_summary = []

            if len(sheet_data) > 0 and "data" in sheet_data[0] and len(sheet_data[0]["data"]) > 0:
                row_data_players = sheet_data[0]["data"][0].get("rowData", [])

            if len(sheet_data) > 1 and "data" in sheet_data[1] and len(sheet_data[1]["data"]) > 0:
                row_data_summary = sheet_data[1]["data"][0].get("rowData", [])

            if not row_data_players or not row_data_summary:
                print(f"🚫 Skipping {team} due to missing sheet data")
                continue

            markdown = format_summary(row_data_summary)
            markdown += "\n\n" + format_markdown(row_data_players)
            sync_note_to_joplin(team, markdown)

        except Exception as e:
            print(f"❌ Failed to sync {team}: {e}")

if __name__ == "__main__":
    main()
