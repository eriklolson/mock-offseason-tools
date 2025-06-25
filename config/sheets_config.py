import os
from config.base import BASE_DIR  # Optional, if needed for path logic
# ==== Team Sheet Config ====


TEAM_SHEETS_CONFIG = os.getenv(
    "TEAM_SHEETS_CONFIG",
    os.path.join(BASE_DIR, "config", "teamsheets.yaml")
)

# # Optional: default headers for HTTP requests
# HEADERS = {"Content-Type": "application/json"}
#
# WORKBOOK_PATH='/home/erik/Desktop/Charlotte.xlsx'