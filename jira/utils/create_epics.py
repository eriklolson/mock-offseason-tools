#!/usr/bin/env python3

import yaml
import subprocess

YAML_FILE = "epics.yml"

with open(YAML_FILE, "r") as f:
    data = yaml.safe_load(f)

epics = data.get("epics", [])

for epic in epics:
    name = epic.get("name")
    summary = epic.get("summary")

    if not name or not summary:
        print(f"⚠️ Skipping epic (missing name or summary): {epic}")
        continue

    cmd = ["jira", "epic", "create", "-n", name, "-s", summary]

    if epic.get("priority"):
        cmd += ["-y", epic["priority"]]

    if epic.get("description"):
        cmd += ["-b", epic["description"]]

    for label in epic.get("labels", []):
        if label:  # skip empty strings
            cmd += ["-l", label]

    print(f"➤ Creating epic: {name}")
    print("↳", " ".join(cmd))
    subprocess.run(cmd)
