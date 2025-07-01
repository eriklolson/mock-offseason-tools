import os
from config.base import BASE_DIR  # Optional, if needed for path logic
# ==== Team Sheet Config ====


TEAM_SHEETS_CONFIG = os.getenv(
    "TEAM_SHEETS_CONFIG",
    os.path.join(BASE_DIR, "config", "teamsheets.yaml")
)

MD_TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "team_sheet_template.md")
# # Optional: default headers for HTTP requests
# HEADERS = {"Content-Type": "application/json"}
#
# WORKBOOK_PATH='/home/erik/Desktop/Charlotte.xlsx'