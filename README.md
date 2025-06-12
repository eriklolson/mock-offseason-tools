# 🏀 mock-offseason-tools

A modular toolkit designed to support syncing and automation tasks for a 2025 NBA mock offseason. This project integrates Google Sheets, Joplin, and Jira to streamline tracking, planning, and execution of mock offseason decisions across all 30 NBA teams.

---

## 📁 Project Structure
mock-offseason-tools
├── chatgpt-sync # Syncs Joplin tables with teams' cap sheets and ChatGPT project notes
├── envs # Micromamba environment definitions for reproducible setups
├── jira-sync # Automates Jira epic and issue creation for tracking development tasks
│ └── jira-sync-config.yml
├── joplin-sync # Syncs Joplin notes for each NBA team with corresponding Google Sheets data
└── env.yml # Top-level environment file for setting up dependencies

## 🧩 Module Overview

- **`chatgpt-sync/`**  
  Integrates ChatGPT-generated outputs with synced cap sheet data and note tables stored in Joplin.

- **`envs/`**  
  Contains Micromamba environment specs used across different modules for isolation and dependency control.

- **`jira-sync/`**  
  Scripts to generate and manage Jira Epics and tasks, organizing development work required to build this sync system.

- **`joplin-sync/`**  
  Automates syncing of structured Markdown tables in Joplin notes using data pulled from private Google Sheets per NBA team.

- **`env.yml`**  
  Unified environment file to install required packages (e.g. `pandas`, `google-auth`, `joplin-api`) for the entire project.

---

## ✅ Status

Actively used to support and automate team-based decision-making during the 2025 NBA mock offseason.
