#!/usr/bin/env python3
import os
import sys
import yaml
import gspread
import requests
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.google_config import GOOGLE_TOKEN, GOOGLE_CREDENTIALS, SCOPES
from config.joplin_config import JOPLIN_API, JOPLIN_TOKEN, JOPLIN_NOTEBOOK_ID
from config.sheets_config import TEAM_SHEETS_CONFIG, MD_TEMPLATE_PATH
from utils.throttle import rate_limited

# Load md_var_map.yaml
with open(os.path.join("config", "md_var_map.yaml"), "r") as f:
    md_var_map = yaml.safe_load(f)


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


def check_joplin_api_available():
    try:
        res = requests.get(f"{JOPLIN_API}/ping", timeout=3)
        if res.status_code != 200:
            raise Exception(f"Unexpected response code: {res.status_code}")
    except Exception as e:
        print(f"❌ Joplin API is not available: {e}")
        exit(1)


def notebook_exists(notebook_id):
    res = requests.get(f"{JOPLIN_API}/folders/{notebook_id}", params={"token": JOPLIN_TOKEN})
    return res.status_code == 200


def get_or_create_note(title, notebook_id):
    search_url = f"{JOPLIN_API}/search?query={title}&type=note&token={JOPLIN_TOKEN}"
    resp = requests.get(search_url)
    for item in resp.json().get("items", []):
        if item.get("title") == title:
            return item["id"]

    create_url = f"{JOPLIN_API}/notes?token={JOPLIN_TOKEN}"
    resp = requests.post(create_url, json={"title": title, "parent_id": notebook_id, "body": ""})
    return resp.json()["id"]


def update_note_body(note_id, markdown):
    url = f"{JOPLIN_API}/notes/{note_id}?token={JOPLIN_TOKEN}"
    return requests.put(url, json={"body": markdown}).status_code == 200


def render_template_with_data(template_str, sheet):
    @rate_limited(0.5)
    def get_range(sheet, cell_range):
        try:
            return sheet.get(cell_range)
        except Exception:
            return []

    @rate_limited(0.5)
    def get_cell(sheet, cell):
        try:
            return sheet.acell(cell).value
        except Exception:
            return ""

    flat_vars = {}
    list_vars = {}

    for section in md_var_map:
        for key, cell_range in md_var_map[section].items():
            if ":" in cell_range:
                list_vars[key] = get_range(sheet, cell_range)
            else:
                flat_vars[key] = get_cell(sheet, cell_range)

    # Build player salary/status table
    player_md = (
        "| # | Player Name | 2025–26 Salary | Status | 2026–27 Salary | Status | 2027–28 Salary | Status |\n"
        "|---|-------------|----------------|--------|----------------|--------|----------------|--------|\n"
    )

    players = list_vars.get("player_name", [])
    sal_26 = list_vars.get("player_sal_26", [])
    sal_27 = list_vars.get("player_sal_27", [])
    sal_28 = list_vars.get("player_sal_28", [])
    stat_26 = list_vars.get("player_stat_26", [])
    stat_27 = list_vars.get("player_stat_27", [])
    stat_28 = list_vars.get("player_stat_28", [])

    for i in range(len(players)):
        name = players[i][0] if i < len(players) else ""
        s26 = sal_26[i][0] if i < len(sal_26) else ""
        s27 = sal_27[i][0] if i < len(sal_27) else ""
        s28 = sal_28[i][0] if i < len(sal_28) else ""
        st26 = stat_26[i][0] if i < len(stat_26) else ""
        st27 = stat_27[i][0] if i < len(stat_27) else ""
        st28 = stat_28[i][0] if i < len(stat_28) else ""

        if name:
            player_md += f"| {i+1} | {name} | {s26} | {st26} | {s27} | {st27} | {s28} | {st28} |\n"

    filled = template_str.replace("{{PLAYER_SALARY_TABLE}}", player_md)

    for key, value in flat_vars.items():
        filled = filled.replace(f"{{{{{key}}}}}", value)

    return filled


def main():
    check_joplin_api_available()

    if not notebook_exists(JOPLIN_NOTEBOOK_ID):
        raise ValueError("❌ Invalid or missing JOPLIN_NOTEBOOK_ID")

    creds = authenticate()
    gc = gspread.authorize(creds)
    teams = load_team_sheets()
    template_str = Path(MD_TEMPLATE_PATH).read_text(encoding="utf-8")


    for team, url in teams.items():
        print(f"📥 Fetching: {team}")
        sheet_id = url.split("/d/")[1].split("/")[0]

        try:
            sheet = gc.open_by_key(sheet_id).worksheet("Roster")
            rendered = render_template_with_data(template_str, sheet)
            note_id = get_or_create_note(team, JOPLIN_NOTEBOOK_ID)
            success = update_note_body(note_id, rendered)
            print(f"{'✅' if success else '❌'} Synced {team}")
        except Exception as e:
            print(f"❌ Failed to sync {team}: {e}")


if __name__ == "__main__":
    main()
