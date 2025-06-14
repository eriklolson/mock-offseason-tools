#!/usr/bin/env python3

import argparse
import yaml
import os
from pathlib import Path

JIRA_CLI_CONFIG_PATH = Path.home() / ".config" / ".jira" / ".config.yml"


def load_config(path='config.yml', project=None):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)

    project_key = project or config.get('default_project')
    if project_key not in config['projects']:
        raise ValueError(f"Project '{project_key}' not found in config.")
    return config['projects'][project_key]

def update_jira_cli_config(project_config):
    # Load existing CLI config
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
    parser.add_argument("--project", type=str, required=True, help="Project key from config.yml (e.g., PROJ2)")
    parser.add_argument("--config", type=str, default="config.yml", help="Path to your config.yml")
    args = parser.parse_args()

    try:
        project_config = load_config(args.config, args.project)
        update_jira_cli_config(project_config)
    except Exception as e:
        print(f"❌ {e}")

if __name__ == "__main__":
    main()
