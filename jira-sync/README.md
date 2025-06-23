🔄 Final Script Logic Summary
Here’s what spreadsheet-joplin-sync.py will do:

Authenticate with Google Sheets API (v4).

For each team spreadsheet:

Open the "Roster" tab.

Extract player salaries by season (2025–26 through 2029–30).

Detect the background color of each salary cell.

Map that color to a contract status marker:

mathematica
Copy
Edit
Red     → CH
Green   → PO
Blue    → TO
Orange  → 10D
Grey    → NG
No Fill → (nothing)
Format each salary cell like TO $9,500,000.

Convert the full table to Markdown.

Sync it to the appropriate Joplin note (title = team name), in the notebook:

bash
Copy
Edit
Mock Offseason/Mock 2025/1. Sheets  
joplin://x-callback-url/openFolder?id=67e975d394dd43e9bde397740bbe821b
