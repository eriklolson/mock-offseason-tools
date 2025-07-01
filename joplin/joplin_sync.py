#!/usr/bin/env python3
import os
import sys
import requests
import yaml
import gspread
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.google_config import GOOGLE_TOKEN, GOOGLE_CREDENTIALS, SCOPES
from config.joplin_config import BASE_DIR, JOPLIN_API, JOPLIN_TOKEN, JOPLIN_NOTEBOOK_ID
from config.sheets_config import TEAM_SHEETS_CONFIG
from joplin.utils.team_markdown_builder import build_team_summary


def authenticate():
    creds = None
    if os.path.exists(GOOGLE_TOKEN):
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(GOOGLE_TOKEN, "w") as token_file:
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
        return "🔴"
    elif rgb_match(r, g, b, (0.6, 0.8, 0.6)):
        return "🟢"
    elif rgb_match(r, g, b, (0.6, 0.6, 0.8)):
        return "🔵"
    elif rgb_match(r, g, b, (1.0, 0.8, 0.6)):
        return "🟡"
    elif rgb_match(r, g, b, (0.85, 0.85, 0.85)):
        return "⚪"
    else:
        return ""


def render_template(template, placeholder_map):
    for placeholder, value in placeholder_map.items():
        template = template.replace(f"{{{{{placeholder}}}}}", value)
    return template


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
    gc = gspread.authorize(creds)

    teams = load_team_sheets()
    for team, url in teams.items():
        print(f"📥 Fetching: {team}")
        sheet_id = url.split("/d/")[1].split("/")[0]
        try:
            sheet_data = get_sheet_data(service, sheet_id)

            row_data_players = []
            if len(sheet_data) > 0 and "data" in sheet_data[0] and len(sheet_data[0]["data"]) > 0:
                row_data_players = sheet_data[0]["data"][0].get("rowData", [])

            if not row_data_players:
                print(f"🚫 Skipping {team} due to missing player rows")
                continue

            spreadsheet = gc.open_by_key(sheet_id)
            sheet = spreadsheet.worksheet("Roster")

            # Load template
            template = build_team_summary(sheet)

            # Map placeholders to values
            placeholder_map = {}
            for i, row in enumerate(row_data_players):
                cells = row.get("values", [])
                if not cells:
                    continue

                name = cells[0].get("formattedValue", "").strip() if len(cells) > 0 else ""
                salary_cell = cells[1] if len(cells) > 1 else {}
                val = salary_cell.get("effectiveValue", {}).get("numberValue")
                salary = f"${val:,.0f}" if val is not None else salary_cell.get("formattedValue", "").strip()

                marker = get_status_marker(salary_cell)
                if marker:
                    salary = f"{marker} {salary}"

                placeholder_map[f"player{i+1}_name"] = name or ""
                placeholder_map[f"player{i+1}_25"] = salary or ""
                placeholder_map[f"player{i+1}_26"] = ""  # Extend if needed

            # Fill in placeholders
            markdown = render_template(template, placeholder_map)

            sync_note_to_joplin(team, markdown)

        except Exception as e:
            print(f"❌ Failed to sync {team}: {e}")


if __name__ == "__main__":
    main()
