#!/usr/bin/env python3

import yaml
import subprocess

YAML_FILE = "epic_issues.yml"

with open(YAML_FILE, "r") as f:
    data = yaml.safe_load(f)

epic_blocks = data.get("epics", [])

for block in epic_blocks:
    epic = block.get("epic")
    issues = block.get("issues", [])

    if not epic or not issues:
        print(f"⚠️ Skipping block with missing epic or issues: {block}")
        continue

    cmd = ["jira", "epic", "add", epic] + issues
    print(f"➤ Adding issues to {epic}: {', '.join(issues)}")
    subprocess.run(cmd)
