#!/usr/bin/env python3

import requests
from config.joplin_config import BASE_DIR, JOPLIN_API, JOPLIN_TOKEN, JOPLIN_NOTEBOOK_ID

# -------------------- NBA Teams --------------------

NBA_TEAMS = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
    "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors",
    "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
    "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
    "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"
]

# -------------------- Markdown Tables --------------------

MARKDOWN_BLOCK = """

|     |     |
| --- | --- | 
| **Cap Space** | /\\{Cap Space} |
| **1st Apron Space** | /\\{1st Apron Space} |
| **2nd Apron Space** | /\\{2nd Apron Space} | 


|     |     |     |     |
| --- | --- | --- | --- |
| **Free Agency Ex­cep­tions** | **Avail­able** | **Remaining** | **Triggers Hard Cap?** |
| **Cap Room Ex­cep­tion** | {YES/NO} | {cre amount} | No  |
| **Bi-An­nu­al Ex­cep­tion (BAE)** | {YES/NO} | {bae amount} | At 1st Apron |
| **Tax­pay­er MLE** | {YES/NO} | {tmle amount} | At 2nd Apron |
| **Full MLE** | {YES/NO} | {fmle amount} | At 1st Apron |

|     |     |
| --- | --- |
| **Trad­ed Play­er Ex­cep­tions** | **Amount** |
| {tpe player} | {tpe amount} |
"""

# -------------------- Joplin Helpers --------------------

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

def append_tables_to_joplin(title, markdown_tables):
    if not JOPLIN_NOTEBOOK_ID:
        print(f"❌ Cannot update note '{title}' – JOPLIN_NOTEBOOK_ID is missing.")
        return
    if not notebook_exists(JOPLIN_NOTEBOOK_ID):
        print(f"❌ Notebook with ID '{JOPLIN_NOTEBOOK_ID}' not found.")
        return

    res = requests.get(
        f"{JOPLIN_API}/folders/{JOPLIN_NOTEBOOK_ID}/notes",
        params={"token": JOPLIN_TOKEN}
    )
    items = [note for note in res.json().get("items", []) if note["title"] == title]

    if not items:
        print(f"❌ Note '{title}' not found in notebook.")
        return

    note = items[0]
    note_id = note["id"]
    parent_id = note.get("parent_id", JOPLIN_NOTEBOOK_ID)
    notebook_path = get_notebook_path(parent_id)

    note_res = requests.get(
        f"{JOPLIN_API}/notes/{note_id}",
        params={"token": JOPLIN_TOKEN}
    )
    if note_res.status_code != 200:
        print(f"❌ Failed to fetch note content for '{title}'.")
        return

    current_body = note_res.json().get("body", "")

    # Check for existing marker to prevent duplicate appends
    if "**Cap Space**" in current_body:
        print(f"⚠️  Tables already present in '{title}', skipping.")
        return

    updated_body = current_body.rstrip() + "\n\n" + markdown_tables.strip()

    update_res = requests.put(
        f"{JOPLIN_API}/notes/{note_id}",
        params={"token": JOPLIN_TOKEN},
        json={"body": updated_body}
    )

    if update_res.status_code != 200:
        print(f"❌ Failed to update note '{title}': {update_res.status_code} {update_res.text}")
        return

    note_url = f"joplin://x-callback-url/openNote?id={note_id}"
    print(f"✅ Appended tables to {notebook_path}/{title} → {note_url}")

# -------------------- Main --------------------

def main():
    if not JOPLIN_TOKEN or not JOPLIN_NOTEBOOK_ID:
        print("❌ Missing JOPLIN_TOKEN or JOPLIN_NOTEBOOK_ID.")
        return

    for team in NBA_TEAMS:
        append_tables_to_joplin(team, MARKDOWN_BLOCK)

if __name__ == "__main__":
    main()
