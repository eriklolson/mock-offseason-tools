# 📝 NBA Trade Checker – Charlotte Hornets Edition

## 📌 Overview
This script checks **NBA trade legality** between the **Charlotte Hornets** and another team based on **2025–26 CBA trade rules**, including:

- Salary-matching bands
- TPE / cap space usage
- Apron-based restrictions (1st and 2nd apron)
- Aggregation restrictions

---

## 🚀 How to Use

```bash
python3 salary_check.py
You'll be prompted to enter:

Other team abbreviation (e.g., BOS)

Charlotte salaries (comma-separated, e.g. 21000000, 5000000)

Other team salaries (comma-separated)

Whether Charlotte is over the second apron (yes / no)

(Optional) TPE or cap space available to Charlotte (ignored if over 2nd apron)

🔒 CBA Compliance Logic
Rule	Enforced?	Notes
Salary Matching Bands	✅	200% + $250K under $7.5M, +$7.75M up to $30M, 125% + $250K over $30M
TPE / Cap Space Absorption	✅	Absorbs salaries ≤ TPE + $250K
Second Apron Restrictions	✅	No aggregation, no TPE/cap usage, only 1-for-1 trades allowed
Both Teams Evaluated	✅	Evaluates legality for Charlotte and the other team

🔧 Example
Legal Trade (under 2nd apron):
text
Copy
Edit
Charlotte salaries: 18000000, 2500000
Other team salaries: 9000000
Over second apron? no
TPE/cap space: 9000000
Illegal Trade (over 2nd apron):
text
Copy
Edit
Charlotte salaries: 18000000, 2500000
Other team salaries: 15000000
Over second apron? yes
Output:

pgsql
Copy
Edit
🚫 Invalid: Charlotte is over the second apron and cannot aggregate multiple salaries.
📁 File Structure
salary_check.py – interactive CLI script

(Optional) README.md – this help doc

🛠 Future Enhancements
 GUI or web interface

 Export to CSV or JSON

 Multi-TPE assignment support

 # Expanded Version 
 For each team (Team A and Team B):
    - Pre-trade First Apron Space (in dollars)
    - Pre-trade Second Apron status (Boolean: True if above 2nd apron before trade)
    - Total Outgoing Salary
    - Total Incoming Salary
    - Cap Space Available
    - Exceptions Used (list of strings: ["TPE", "MLE", "Minimum", etc.])
    - Is Aggregating Players? (Boolean)
    - List of Players Acquired with Years of Experience
🔍 Constants
plaintext
Copy
Edit
FIRST_APRON_THRESHOLD = $178,655,000 (example for 2025)
SECOND_APRON_THRESHOLD = $189,485,000 (example for 2025)

MINIMUM_SALARY_BY_YEARS = {
    0: 1272870, 1: 2048494, 2: 2296274, 3: 2378870, 4: 2461463,
    5: 2667947, 6: 2874436, 7: 3080921, 8: 3287409, 9: 3303774, 10: 3634153
}
✅ Pseudocode Logic
plaintext
Copy
Edit
function check_trade_legality(team_data_A, team_data_B):
    for each team in [team_data_A, team_data_B]:

        OUT = team.outgoing_salary
        IN = team.incoming_salary
        PRE_APRON_SPACE = team.pre_first_apron_space
        USING_EXCEPTIONS = team.exceptions_used
        IS_AGGREGATING = team.is_aggregating
        CAP_SPACE = team.cap_space
        PLAYER_YOS = team.incoming_player_years_of_experience
        IS_ABOVE_SECOND_APRON = team.is_above_second_apron_pre

        POST_FIRST_APRON_SPACE = PRE_APRON_SPACE - (IN - OUT)

        # --------------------------
        # 🔴 Case 1: Team is above 2nd Apron before trade
        if IS_ABOVE_SECOND_APRON:

            if IN > OUT:
                return "❌ Trade Illegal: Cannot take back more salary above 2nd apron"

            if IS_AGGREGATING:
                return "❌ Trade Illegal: Cannot aggregate salaries above 2nd apron"

            for exc in USING_EXCEPTIONS:
                if exc != "Minimum":
                    return f"❌ Trade Illegal: Cannot use {exc} exception above 2nd apron"

            for yos in PLAYER_YOS:
                if IN > MINIMUM_SALARY_BY_YEARS[yos]:
                    return "❌ Trade Illegal: Incoming salary not eligible for minimum exception"

        # --------------------------
        # 🟡 Case 2: Team is below 1st Apron before AND after trade
        elif PRE_APRON_SPACE > 0 and POST_FIRST_APRON_SPACE > 0:
            # Full flexibility: trade is likely legal. Continue to salary matching check later.
            continue

        # --------------------------
        # 🟠 Case 3: Team is below 1st Apron BEFORE but ABOVE after trade
        elif PRE_APRON_SPACE > 0 and POST_FIRST_APRON_SPACE <= 0:

            if IS_AGGREGATING:
                return "❌ Trade Illegal: Cannot aggregate if crossing 1st apron due to trade"

            for exc in USING_EXCEPTIONS:
                if exc != "Minimum":
                    return f"❌ Trade Illegal: Cannot use {exc} exception if crossing 1st apron"

        # --------------------------
        # Match salaries according to standard trade rules
        legality, limit = evaluate_salary_matching(OUT, IN)

        if not legality:
            return f"❌ Trade Illegal: Incoming salary (${IN}) exceeds allowable matching limit (${limit})"

    return "✅ Trade is CBA Legal for both teams"
🔢 Salary Matching Function (simplified pseudocode)
plaintext
Copy
Edit
function evaluate_salary_matching(outgoing, incoming):
    if outgoing <= 7,501,817.73:
        limit = (outgoing * 2) + 250,000
    elif outgoing <= 30,007,270.94:
        limit = outgoing + 7,751,817.73
    else:
        limit = (outgoing * 1.25) + 250,000

    if incoming <= limit:
        return True, limit
    else:
        return False, limit
