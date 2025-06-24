#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

# Load .env and pull token + API address
load_dotenv()
JOPLIN_API = os.getenv("JOPLIN_API", "http://127.0.0.1:41184")
JOPLIN_TOKEN = os.getenv("JOPLIN_TOKEN")

if not JOPLIN_TOKEN:
    print("❌ JOPLIN_TOKEN not set in .env")
    exit(1)

def get_all_folders():
    all_folders = []
    page = 1

    while True:
        res = requests.get(
            f"{JOPLIN_API}/folders",
            params={
                "token": JOPLIN_TOKEN,
                "page": page
            }
        )

        if res.status_code != 200:
            print(f"❌ Request failed: {res.status_code} - {res.text}")
            break

        data = res.json()
        items = data.get("items", [])
        all_folders.extend(items)

        if data.get("has_more"):
            page += 1
        else:
            break

    return all_folders

def main():
    folders = get_all_folders()
    if not folders:
        print("⚠️ No folders returned.")
        return

    print(f"📁 Found {len(folders)} folders:\n")
    for f in folders:
        print(f"- {f['title']} (ID: {f['id']})")

if __name__ == "__main__":
    main()
