import os
from config.base import BASE_DIR  # Optional, if needed for path logic

# ==== Joplin Config ====
JOPLIN_API = os.getenv("JOPLIN_API", "http://127.0.0.1:41184")
JOPLIN_TOKEN = os.getenv("JOPLIN_TOKEN")
JOPLIN_NOTEBOOK_ID = os.getenv("JOPLIN_NOTEBOOK_ID")
TEMPLATE_PATH = os.path.join("templates", "team_sheet_template.md")