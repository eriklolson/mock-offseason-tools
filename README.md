# 🏀 mock-offseason-tools

A modular toolkit designed to support syncing and automation tasks for a 2025 NBA mock offseason. This project integrates Google Sheets (or locally downloaded copies of them), Joplin, and Jira to streamline tracking, planning, and execution of mock offseason decisions.

---
├── auth
│   └── secrets
│       └── oauth
│           └── credentials.json
                      jira
                          config.yml
├── chatgpt-sync
├── config
│   └── team_sheets.yaml
├── environment.yml
├── helper-scripts
│   ├── README.md
│   └── salary_check.py
├── jira-sync
│   ├── create_jira_from_yaml.py
│   ├── jira-sync-config.yml
│   ├── proj-switcher.py
│   └── README.md
├── joplin-sync
│   ├── generate_team_sheets_yaml.py
│   └── spreadsheet-joplin-sync.py
├── main.py
└── README.md


## 🧩 Module Overview

- **`chatgpt-sync/`**  
  Integrates ChatGPT-generated outputs with synced cap sheet data and note tables stored in Joplin.

- **`envs/`**  
  Contains Micromamba environment specs used across different modules for isolation and dependency control.

- **`joplin-sync/`**  
  Automates syncing of Markdown tables in Joplin notes using data pulled from private Google Sheets per NBA team; but also optionally can sync a local copy of such spreadsheet.

- **`jira-sync/`**  
  Automates jira issues for expanding this app and for mock offseason tasks

- **`environment.yml`**  
  Unified environment file to install required packages (e.g. `pandas`, `google-auth`, `joplin-api`) for the entire project.

---

## Statusz

Actively used to support and automate team-based decision-making during the 2025 NBA mock offseason.
