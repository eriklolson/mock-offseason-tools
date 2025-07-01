#!/usr/bin/env python3
import os
import sys
import yaml
import requests
import gspread
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Set up import paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.google_config import GOOGLE_TOKEN, GOOGLE_CREDENTIALS, SCOPES
from config.joplin_config import JOPLIN_API, JOPLIN_TOKEN, JOPLIN_NOTEBOOK_ID
from config.sheets_config import TEAM_SHEETS_CONFIG, MD_TEMPLATE_PATH


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


def load_md_var_map():
    with open("config/md_var_map.yaml", "r") as f:
        return yaml.safe_load(f)


def safe_get(sheet, cell):
    try:
        return sheet.acell(cell).value or ""
    except Exception:
        return ""


def safe_col_range(sheet, col_range):
    try:
        return [cell.value.strip() if cell.value else "" for cell in sheet.range(col_range)]
    except Exception:
        return []


def format_dollar(val):
    try:
        return f"${float(val.replace('$', '').replace(',', '')):,.0f}"
    except:
        return val or ""


def get_or_create_note(title, notebook_id):
    search_url = f"{JOPLIN_API}/search?query={title}&type=note&token={JOPLIN_TOKEN}"
    resp = requests.get(search_url)
    results = resp.json().get("items", [])

    for item in results:
        if item.get("title") == title:
            return item["id"]

    create_url = f"{JOPLIN_API}/notes?token={JOPLIN_TOKEN}"
    resp = requests.post(create_url, json={"title": title, "parent_id": notebook_id, "body": ""})
    return resp.json()["id"]


def update_note_body(note_id, markdown):
    update_url = f"{JOPLIN_API}/notes/{note_id}?token={JOPLIN_TOKEN}"
    resp = requests.put(update_url, json={"body": markdown})
    return resp.status_code == 200


def build_filled_markdown(sheet, var_map):
    # Load base template
    template_path = Path(MD_TEMPLATE_PATH)
    base_md = template_path.read_text(encoding="utf-8")

    # Insert all single-cell dynamic values
    for section in ["cap_variables", "exceptions"]:
        for var, cell in var_map.get(section, {}).items():
            val = format_dollar(safe_get(sheet, cell))
            base_md = base_md.replace(f"{{{{{var}}}}}", val)

    # Handle player salary table
    names = safe_col_range(sheet, var_map["payroll"]["player_name"])
    s25s = safe_col_range(sheet, var_map["payroll"]["player_sal_26"])
    s26s = safe_col_range(sheet, var_map["payroll"]["player_sal_27"])

    rows = []
    for i, (name, s25, s26) in enumerate(zip(names, s25s, s26s), 1):
        if name:
            row = f"| {i} | {name} | {format_dollar(s25)} | {format_dollar(s26)} |"
            rows.append(row)

    salary_table = (
        "| # | Player Name | 2025–26 Salary | 2026–27 Salary |\n"
        "|---|-------------|----------------|----------------|\n"
        + "\n".join(rows)
    )

    base_md = base_md.replace("{{PLAYER_SALARY_TABLE}}", salary_table)

    return base_md


def main():
    creds = authenticate()
    gc = gspread.authorize(creds)
    var_map = load_md_var_map()
    teams = load_team_sheets()

    for team, url in teams.items():
        print(f"📥 Fetching: {team}")
        try:
            sheet_id = url.split("/d/")[1].split("/")[0]
            spreadsheet = gc.open_by_key(sheet_id)
            sheet = spreadsheet.worksheet("Roster")
            final_md = build_filled_markdown(sheet, var_map)
            note_id = get_or_create_note(team, JOPLIN_NOTEBOOK_ID)
            success = update_note_body(note_id, final_md)
            print(f"{'✅' if success else '❌'} Synced {team}")
        except Exception as e:
            print(f"❌ Failed to sync {team}: {e}")


if __name__ == "__main__":
    main()
