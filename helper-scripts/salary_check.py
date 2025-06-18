import re

def parse_salary(s):
    return float(re.sub(r"[^\d.]", "", s.strip()))

def parse_salary_list(salary_str):
    return [parse_salary(s) for s in salary_str.split(",") if s.strip()]

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

def absorb_with_tpe_or_space(salaries, absorber_pool):
    absorbed = []
    remaining = []
    available = absorber_pool

    for s in salaries:
        if s <= available + 250_000:
            absorbed.append(s)
            available -= s  # absorbed into TPE/space
        else:
            remaining.append(s)

    return absorbed, remaining, absorber_pool - available

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

    print(f"\nEnter player salaries for each side as comma-separated values:")
    charlotte_salaries = parse_salary_list(input(f"{team_a} is sending out: "))
    other_team_salaries = parse_salary_list(input(f"{team_b} is sending out: "))

    tpe_input = input("\nEnter TPE or Cap Space amount available to Charlotte (or leave blank): ").strip()
    tpe_pool = parse_salary(tpe_input) if tpe_input else 0.0

    absorbed, remaining, absorbed_total = absorb_with_tpe_or_space(other_team_salaries, tpe_pool)

    print(f"\n💼 TPE / Cap Space Application")
    print(f"Available: ${tpe_pool:,.2f}")
    print(f"Absorbed Salaries: {[f'${s:,.2f}' for s in absorbed]}")
    print(f"Remaining for Matching: {[f'${s:,.2f}' for s in remaining]}")
    print(f"Total Absorbed: ${absorbed_total:,.2f}")

    outgoing_total = sum(charlotte_salaries)
    incoming_total = sum(remaining)

    print(f"\n🔁 Trade Summary: {team_a} ⇄ {team_b}")
    print(f"{team_a} sends ${outgoing_total:,.2f}, receives ${sum(other_team_salaries):,.2f} total")
    print(f"→ of which ${absorbed_total:,.2f} is absorbed via TPE/Cap Space")
    print(f"{team_b} sends ${sum(other_team_salaries):,.2f}, receives ${outgoing_total:,.2f}")

    evaluate_legality(team_a, outgoing_total, incoming_total)
    evaluate_legality(team_b, sum(other_team_salaries), outgoing_total)
