import os
import requests
from dotenv import load_dotenv

load_dotenv()

JOPLIN_API = os.getenv("JOPLIN_API", "http://127.0.0.1:41184")
JOPLIN_TOKEN = os.getenv("JOPLIN_TOKEN")
TARGET_PATH = "Mock Offseason/Mock 2025/1. Sheets"  # Adjust if needed

def list_notebooks():
    url = f"{JOPLIN_API}/folders"
    res = requests.get(url, params={"token": JOPLIN_TOKEN})
    res.raise_for_status()
    return res.json().get("items", [])  # ✅ return just the list of folders

def build_path_map():
    path_map = {}

    def recurse(folder, prefix=""):
        path = f"{prefix}/{folder['title']}".strip("/")
        path_map[path] = folder["id"]

        res = requests.get(
            f"{JOPLIN_API}/folders/{folder['id']}/folders",
            params={"token": JOPLIN_TOKEN}
        )
        if res.status_code == 200:
            children = res.json().get("items", [])
            for child in children:
                recurse(child, path)

    # Get top-level folders
    res = requests.get(f"{JOPLIN_API}/folders", params={"token": JOPLIN_TOKEN})
    res.raise_for_status()
    for folder in res.json().get("items", []):
        recurse(folder)

    return path_map

def update_dotenv(key, value):
    path = ".env"
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(f"{key}={value}\n")
        return

    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w") as f:
        found = False
        for line in lines:
            if line.startswith(f"{key}="):
                f.write(f"{key}={value}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"{key}={value}\n")

def main():
    path_map = build_path_map()
    notebook_id = path_map.get(TARGET_PATH)
    if notebook_id:
        print(f"✅ Found notebook: '{TARGET_PATH}'\nID: {notebook_id}")
        update_dotenv("JOPLIN_NOTEBOOK_ID", notebook_id)
        print("✅ Updated .env with JOPLIN_NOTEBOOK_ID")
    else:
        print(f"❌ Notebook path not found: {TARGET_PATH}")
        print("🔍 Available paths:")
        for p in sorted(path_map):
            print(f"  • {p}")

if __name__ == "__main__":
    main()
