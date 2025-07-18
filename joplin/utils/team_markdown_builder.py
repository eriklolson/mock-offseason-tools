import sys
import locale
import requests
from pathlib import Path

# Dynamically add the project root to sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from config.joplin_config import JOPLIN_API, JOPLIN_TOKEN, JOPLIN_NOTEBOOK_ID
from config.sheets_config import MD_TEMPLATE_PATH

def build_team_summary(sheet=None):
    template_path = Path(MD_TEMPLATE_PATH)
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "**Error:** team sheet template not found at expected path."

def get_teams():
    return [
        "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
        "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors",
        "Houston Rockets", "Indiana Pacers", "LA Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
        "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
        "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
        "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"
    ]

def get_or_create_note(title, notebook_id):
    search_url = f"{JOPLIN_API}/search?query={title}&type=note&token={JOPLIN_TOKEN}"
    resp = requests.get(search_url)
    results = resp.json().get("items", [])

    for item in results:
        if item.get("title") == title:
            return item["id"]

    # Create the note if it doesn't exist
    create_url = f"{JOPLIN_API}/notes?token={JOPLIN_TOKEN}"
    resp = requests.post(create_url, json={
        "title": title,
        "parent_id": notebook_id,
        "body": ""
    })
    return resp.json()["id"]

def get_note_body(note_id):
    resp = requests.get(f"{JOPLIN_API}/notes/{note_id}", params={"token": JOPLIN_TOKEN})
    if resp.status_code == 200:
        return resp.json().get("body", "")
    return ""

def should_update_note(existing_body, new_template):
    # Check for any placeholders in the template that aren't already present in the current body
    import re
    new_placeholders = set(re.findall(r"\{\{(\w+)\}\}", new_template))
    existing_placeholders = set(re.findall(r"\{\{(\w+)\}\}", existing_body))
    return not new_placeholders.issubset(existing_placeholders)

def update_note_body(note_id, markdown):
    update_url = f"{JOPLIN_API}/notes/{note_id}?token={JOPLIN_TOKEN}"
    resp = requests.put(update_url, json={"body": markdown})
    return resp.status_code == 200

def main():
    markdown_template = build_team_summary()
    teams = get_teams()

    for team in teams:
        note_id = get_or_create_note(team, JOPLIN_NOTEBOOK_ID)
        current_body = get_note_body(note_id)

        if should_update_note(current_body, markdown_template):
            success = update_note_body(note_id, markdown_template)
            print(f"{'✅' if success else '❌'} Updated {team} with new template.")
        else:
            print(f"⏩ Skipped {team} — all placeholders already present.")

if __name__ == "__main__":
    main()
