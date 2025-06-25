#!/usr/bin/env python3

import openpyxl
import requests
import sys
import os
from dotenv import load_dotenv
import os
import sys
import openpyxl
import requests
from dotenv import load_dotenv

from joplin import (
    JOPLIN_API, JOPLIN_TOKEN, JOPLIN_NOTEBOOK_ID,
    WORKBOOK_PATH as DEFAULT_WORKBOOK_PATH  # <- this line fixes the error
)

# Markdown template with dynamic TPE rows inserted via {TPE_BLOCK}
TEMPLATE = """|     |     |
| --- | --- |
| **Salary for Cap** | {Salary for Cap} |
| **Cap Space** | {Cap Space} |
| **1st Apron Space** | {1st Apron Space} |
| **2nd Apron Space** | {2nd Apron Space} |

|     |     |     |     |
| --- | --- | --- | --- |
| **Free Agency Exceptions** | **Available?** | **Remaining** | **Triggers Hard Cap?** |
| **Cap Room Exception** | {Cap Room Exception} | – | No  |
| **Bi-Annual Exception (BAE)** | {Bi-Annual Exception} | {BAE Amount} | At 1st Apron |
| **Taxpayer MLE** | {Taxpayer MLE} | {TMLE Amount} | At 2nd Apron |
| **Full MLE** | {Full MLE} | {FMLE Amount} | At 1st Apron |

{TPE_BLOCK}
"""

# Cell locations for expected values
CELL_MAP = {
    "Salary for Cap": "Q3",
    "Cap Space": "Q4",
    "1st Apron Space": "Q6",
    "2nd Apron Space": "Q7",
    "Cap Room Exception": "Q11",
    "Bi-Annual Exception": "Q12",
    "Taxpayer MLE": "Q13",
    "Full MLE": "Q14",
    "BAE Amount": "S12",
    "TMLE Amount": "S13",
    "FMLE Amount": "S14"
}


def extract_team_data(sheet):
    values = {}
    missing = []
    for field, cell in CELL_MAP.items():
        try:
            val = sheet[cell].value
            values[field] = str(val).strip() if val is not None else f"{{{field}}}"
            if values[field] == f"{{{field}}}":
                missing.append(cell)
        except:
            values[field] = f"{{{field}}}"
            missing.append(cell)
    return values, missing


def extract_tpes(sheet, start_row=17, end_row=30):
    tpe_rows = ["| **Traded Player Exceptions** | **Amount** |", "| --- | --- |"]
    found = False
    for row in range(start_row, end_row + 1):
        player = sheet[f"Q{row}"].value
        amount = sheet[f"R{row}"].value
        if player and amount:
            tpe_rows.append(f"| {str(player).strip()} | {str(amount).strip()} |")
            found = True
    if not found:
        tpe_rows.append("| – | – |")
    return "\n".join(tpe_rows)


def get_note_by_title(title):
    params = {"token": JOPLIN_TOKEN, "query": title, "type": "note"}
    res = requests.get(f"{JOPLIN_API}/search", params=params)
    res.raise_for_status()
    notes = res.json().get("items", [])
    return notes[0] if notes else None


def create_note(title, body):
    data = {
        "token": JOPLIN_TOKEN,
        "title": title,
        "body": body,
        "parent_id": JOPLIN_NOTEBOOK_ID
    }
    r = requests.post(f"{JOPLIN_API}/notes", json=data)
    r.raise_for_status()
    print(f"🆕 Created note for {title}")


def update_note(note_id, body):
    data = {"token": JOPLIN_TOKEN, "body": body}
    r = requests.put(f"{JOPLIN_API}/notes/{note_id}", json=data)
    r.raise_for_status()
    print(f"✅ Updated note {note_id}")


def main():
    # Support CLI override of workbook path
    workbook_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WORKBOOK_PATH
    if not os.path.exists(workbook_path):
        print(f"❌ Workbook not found: {workbook_path}")
        sys.exit(1)

    wb = openpyxl.load_workbook(workbook_path, data_only=True)

    for sheet in wb.worksheets:
        team_name = sheet.title
        values, missing = extract_team_data(sheet)
        tpe_block = extract_tpes(sheet)
        content = TEMPLATE.format(**values, TPE_BLOCK=tpe_block)

        note = get_note_by_title(team_name)
        if note:
            update_note(note["id"], content)
        else:
            create_note(team_name, content)

        if missing:
            print(f"⚠️  {team_name}: Missing data for cells {', '.join(missing)}")


if __name__ == "__main__":
    main()