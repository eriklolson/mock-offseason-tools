#!/usr/bin/env python3

import argparse
import yaml
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Load JIRA CLI config path from .env or use default
JIRA_CLI_CONFIG_PATH = Path(
    os.getenv("JIRA_CLI_CONFIG_PATH", Path.home() / ".config" / ".jira" / ".config.yml")
)

def load_full_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def select_project_interactively(projects):
    print("\n📋 Available Projects:")
    for i, key in enumerate(projects, 1):
        print(f"  [{i}] {key}")

    while True:
        choice = input("\nSelect a project number: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(projects)):
            print("❌ Invalid selection. Try again.")
            continue
        return list(projects.keys())[int(choice) - 1]

def update_jira_cli_config(project_config):
    if not JIRA_CLI_CONFIG_PATH.exists():
        raise FileNotFoundError(f"{JIRA_CLI_CONFIG_PATH} does not exist")

    with open(JIRA_CLI_CONFIG_PATH, 'r') as f:
        cli_config = yaml.safe_load(f)

    cli_config['endpoint'] = project_config['base_url']
    cli_config['project'] = project_config['project_key']

    with open(JIRA_CLI_CONFIG_PATH, 'w') as f:
        yaml.safe_dump(cli_config, f)

    print(f"✅ Updated CLI config to project: {project_config['project_key']}")

def main():
    parser = argparse.ArgumentParser(description="Switch JIRA CLI active project.")
    parser.add_argument("--project", type=str, help="Project key from config.yml (e.g., PROJ2)")
    parser.add_argument("--config", type=str, default=os.getenv("JIRA_PROJECT_CONFIG", "config.yml"), help="Path to your config.yml")
    args = parser.parse_args()

    try:
        config = load_full_config(args.config)
        projects = config.get('projects', {})

        if not args.project:
            args.project = select_project_interactively(projects)

        if args.project not in projects:
            raise ValueError(f"Project '{args.project}' not found in config.")

        project_config = projects[args.project]
        update_jira_cli_config(project_config)

    except Exception as e:
        print(f"❌ {e}")

if __name__ == "__main__":
    main()
