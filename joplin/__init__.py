#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load .env variables into the environment
load_dotenv()

# Resolve base directory relative to project structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==== Joplin Config ====
JOPLIN_API = os.getenv("JOPLIN_API", "http://127.0.0.1:41184")
JOPLIN_TOKEN = os.getenv("JOPLIN_TOKEN")
JOPLIN_NOTEBOOK_ID = os.getenv("JOPLIN_NOTEBOOK_ID")

# ==== Google Sheets Auth Config ====
CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CREDENTIALS",
    os.path.join(BASE_DIR, "auth/secrets/oauth/credentials.json")
)

TOKEN_PATH = os.getenv(
    "GOOGLE_TOKEN_PATH",
    os.path.join(BASE_DIR, "auth/secrets/oauth/.token.json")
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

# ==== Team Sheet Config ====
TEAM_SHEETS_CONFIG = os.getenv(
    "TEAM_SHEETS_CONFIG",
    os.path.join(BASE_DIR, "config", "teamsheets.yaml")
)

# Optional: default headers for HTTP requests
HEADERS = {"Content-Type": "application/json"}

WORKBOOK_PATH='/home/erik/Desktop/Charlotte.xlsx'