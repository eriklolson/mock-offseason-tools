import locale
locale.setlocale(locale.LC_ALL, '')

def format_dollar(amount):
    try:
        num = float(str(amount).replace("$", "").replace(",", ""))
        return f"${num:,.0f}"
    except (ValueError, TypeError):
        return amount or ""

def safe_get(sheet, cell_ref):
    try:
        return sheet.acell(cell_ref).value or ""
    except Exception:
        return ""

def build_team_summary(sheet):
    # Safely extract cap numbers
    salary_for_cap     = format_dollar(safe_get(sheet, 'C4'))
    cap_space          = format_dollar(safe_get(sheet, 'C5'))
    first_apron_space  = format_dollar(safe_get(sheet, 'C6'))
    second_apron_space = format_dollar(safe_get(sheet, 'C7'))

    # Safely extract exception info
    exceptions = {
        "Cap Room Exception": {
            "available": safe_get(sheet, 'B10'),
            "amount": format_dollar(safe_get(sheet, 'C10')),
            "trigger": "No"
        },
        "Bi-Annual Exception (BAE)": {
            "available": safe_get(sheet, 'B11'),
            "amount": format_dollar(safe_get(sheet, 'C11')),
            "trigger": "At 1st Apron"
        },
        "Taxpayer MLE": {
            "available": safe_get(sheet, 'B12'),
            "amount": format_dollar(safe_get(sheet, 'C12')),
            "trigger": "At 2nd Apron"
        },
        "Full MLE": {
            "available": safe_get(sheet, 'B13'),
            "amount": format_dollar(safe_get(sheet, 'C13')),
            "trigger": "At 1st Apron"
        },
    }

    # Extract up to 10 TPEs (skip blanks)
    try:
        tpe_players_range = sheet.range("B20:B29")
        tpe_amounts_range = sheet.range("C20:C29")
    except Exception:
        tpe_players_range = []
        tpe_amounts_range = []

    tpes = []
    for player_cell, amount_cell in zip(tpe_players_range, tpe_amounts_range):
        player = player_cell.value.strip() if player_cell.value else ""
        amount = amount_cell.value.strip() if amount_cell.value else ""
        if player:
            tpes.append({"player": player, "amount": amount})

    # Markdown: Cap Summary
    cap_summary_md = f"""\
|     |     |
| --- | --- |
| **Salary for Cap** | {salary_for_cap} |
| **Cap Space** | {cap_space} |
| **1st Apron Space** | {first_apron_space} |
| **2nd Apron Space** | {second_apron_space} |
"""

    # Markdown: Exceptions
    exceptions_md = """\
|     |     |     |     |
| --- | --- | --- | --- |
| **Free Agency Ex­cep­tions** | **Avail­able?** | **Remaining** | **Triggers Hard Cap?** |
""" + "\n".join(
        f"| **{label}** | {data['available']} | {data['amount']} | {data['trigger']} |"
        for label, data in exceptions.items()
    )

    # Markdown: TPEs
    tpe_md = """\
|     |     |
| --- | --- |
| **Trad­ed Play­er Ex­cep­tions** | **Amount** |
""" + (
        "\n".join(f"| {tpe['player']} | {format_dollar(tpe['amount'])} |" for tpe in tpes)
        if tpes else "| No TPEs available | – |"
    )

    return "\n\n".join([cap_summary_md, exceptions_md, tpe_md])
