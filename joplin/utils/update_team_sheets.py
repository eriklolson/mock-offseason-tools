#!/usr/bin/env python3

import argparse
import os
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import requests

from config.joplin_config import JOPLIN_API, JOPLIN_TOKEN, JOPLIN_NOTEBOOK_ID

TEMPLATE_PATH = os.path.join("templates", "team_sheet_template.md")

def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_note_id_by_title(title):
    res = requests.get(f"{JOPLIN_API}/search", params={
        "query": title,
        "type": "note",
        "token": JOPLIN_TOKEN
    })
    items = res.json().get("items", [])
    for item in items:
        if item["title"].lower() == title.lower():
            return item["id"]
    return None

def init_template(team_name):
    template = load_template().replace("{{team_name}}", team_name)
    note_id = get_note_id_by_title(team_name)
    if not note_id:
        print(f"❌ Note not found: {team_name}")
        return

    res = requests.get(f"{JOPLIN_API}/notes/{note_id}", params={"token": JOPLIN_TOKEN})
    body = res.json().get("body", "")
    if "{{cap_space}}" in body:
        print(f"⚠️  Template already exists in '{team_name}', skipping.")
        return

    updated_body = body.rstrip() + "\n\n" + template
    put = requests.put(f"{JOPLIN_API}/notes/{note_id}", params={"token": JOPLIN_TOKEN}, json={
        "body": updated_body
    })
    print(f"✅ Inserted template into {team_name} → joplin://x-callback-url/openNote?id={note_id}")

def fill_template(spreadsheet_path, team_name):
    print(f"🔧 (stub) Would load spreadsheet: {spreadsheet_path}")
    print(f"🔧 (stub) Would extract values using cell ranges from YAML and fill placeholders for: {team_name}")
    # This will be implemented in Step 3
    # Plan:
    # - Load cell range mappings from YAML
    # - Load .xlsx data using openpyxl/pandas
    # - Replace placeholders in the loaded Markdown template
    # - Update the Joplin note body

def main():
    parser = argparse.ArgumentParser(description="Update Joplin Team Sheets with Markdown templates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init-template", help="Insert empty template with placeholders")
    init_cmd.add_argument("--team", required=True, help="Team name (must match Joplin note title)")

    fill_cmd = subparsers.add_parser("fill-template", help="Fill template with spreadsheet data")
    fill_cmd.add_argument("--spreadsheet", required=True, help="Path to .xlsx spreadsheet")
    fill_cmd.add_argument("--team", required=True, help="Team name (must match Joplin note title)")

    args = parser.parse_args()

    if args.command == "init-template":
        init_template(args.team)
    elif args.command == "fill-template":
        fill_template(args.spreadsheet, args.team)

if __name__ == "__main__":
    main()
