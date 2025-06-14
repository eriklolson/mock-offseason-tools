import re

def parse_salary(s):
    if isinstance(s, (int, float)):
        return float(s)
    return float(re.sub(r"[^\d.]", "", s))

def lookup_team_name(abbr):
    teams = {
        "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "BKN": "Brooklyn Nets",
        "CHA": "Charlotte Hornets", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
        "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons",
        "GSW": "Golden State Warriors", "HOU": "Houston Rockets", "IND": "Indiana Pacers",
        "LAC": "L.A. Clippers", "LAL": "L.A. Lakers", "MEM": "Memphis Grizzlies",
        "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
        "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder",
        "ORL": "Orlando Magic", "PHI": "Philadelphia 76ers", "PHX": "Phoenix Suns",
        "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings", "SAS": "San Antonio Spurs",
        "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards"
    }
    return teams.get(abbr.upper(), f"[Unknown: {abbr.upper()}]")

def evaluate_legality(team_name, outgoing, incoming):
    if outgoing <= 0:
        print(f"❌ {team_name} has invalid outgoing salary.")
        return False, 0.0, "", 0.0

    if outgoing <= 7_501_817.73:
        limit = (outgoing * 2) + 250_000
        rule = "Can bring back up to 200% more + $250,000"
        formula = f"({outgoing:,.2f} × 2) + 250,000"
    elif outgoing <= 30_007_270.94:
        limit = outgoing + 7_751_817.73
        rule = "Can bring back up to $7,751,817.73 more"
        formula = f"{outgoing:,.2f} + 7,751,817.73"
    else:
        limit = (outgoing * 1.25) + 250_000
        rule = "Can bring back up to 125% more + $250,000"
        formula = f"({outgoing:,.2f} × 1.25) + 250,000"

    delta = incoming - outgoing
    over = max(0, incoming - limit)

    print(f"\n🔍 {team_name} Perspective")
    print(f"------------------------------")
    print(f"Sends Out:        ${outgoing:,.2f}")
    print(f"Takes In:         ${incoming:,.2f}")
    print(f"Net Change:       {'+' if delta >= 0 else ''}${delta:,.2f} ({'adds salary' if delta > 0 else 'saves salary' if delta < 0 else 'no change'})")
    print(f"Matching Rule:    {rule}")
    print(f"Formula Used:     {formula}")
    print(f"Limit:            ${limit:,.2f}")

    if incoming <= limit:
        print("✅ Trade is legal under salary-matching rules.")
        return True, limit, formula, 0.0
    else:
        print("❌ Trade is NOT legal under salary-matching rules.")
        print(f"→ Must reduce incoming salary by at least ${over:,.2f}")
        return False, limit, formula, over

if __name__ == "__main__":
    print("🏀 NBA Trade Checker: Charlotte Hornets + Another Team")
    print("------------------------------------------------------")
    team_b_abbr = input("Enter Team B abbreviation (e.g., BOS, LAL): ").strip().upper()
    team_a = "Charlotte Hornets"
    team_b = lookup_team_name(team_b_abbr)

    outgoing = input(f"Enter salary {team_a} is sending out: ")
    incoming = input(f"Enter salary {team_a} is receiving from {team_b}: ")

    os = parse_salary(outgoing)
    inc = parse_salary(incoming)

    print(f"\n🔁 Trade Summary: {team_a} ⇄ {team_b}")
    print(f"{team_a} sends ${os:,.2f}, receives ${inc:,.2f}")
    print(f"{team_b} sends ${inc:,.2f}, receives ${os:,.2f}")

    # Evaluate for both teams
    evaluate_legality(team_a, os, inc)
    evaluate_legality(team_b, inc, os)
