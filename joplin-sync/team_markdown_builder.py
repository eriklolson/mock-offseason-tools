import locale
locale.setlocale(locale.LC_ALL, '')

def format_dollar(amount):
    try:
        num = float(str(amount).replace("$", "").replace(",", ""))
        return f"${num:,.0f}"
    except (ValueError, TypeError):
        return amount or ""

def build_team_summary(sheet):
    # Basic Cap Overview
    salary_for_cap     = format_dollar(sheet.acell('Q6').value)
    cap_space          = format_dollar(sheet.acell('Q7').value)
    first_apron_space  = format_dollar(sheet.acell('Q8').value)
    second_apron_space = format_dollar(sheet.acell('Q9').value)

    # Exceptions Table
    exceptions = {
        "Cap Room Exception": {
            "available": sheet.acell('R13').value,
            "amount": format_dollar(sheet.acell('T13').value),
            "trigger": "No"
        },
        "Bi-Annual Exception (BAE)": {
            "available": sheet.acell('R14').value,
            "amount": format_dollar(sheet.acell('T14').value),
            "trigger": "At 1st Apron"
        },
        "Taxpayer MLE": {
            "available": sheet.acell('R15').value,
            "amount": format_dollar(sheet.acell('T15').value),
            "trigger": "At 2nd Apron"
        },
        "Full MLE": {
            "available": sheet.acell('R16').value,
            "amount": format_dollar(sheet.acell('T16').value),
            "trigger": "At 1st Apron"
        },
    }

    # TPE Extraction
    tpe_players_range = sheet.range("S21:S31")
    tpe_amounts_range = sheet.range("U21:U31")

    tpes = []
    for player_cell, amount_cell in zip(tpe_players_range, tpe_amounts_range):
        player = player_cell.value.strip() if player_cell.value else ""
        amount = amount_cell.value.strip() if amount_cell.value else ""
        if player:
            tpes.append({"player": player, "amount": amount})

    # Cap Summary Table
    cap_summary_md = f"""\
|     |     |
| --- | --- |
| **Salary for Cap** | {salary_for_cap} |
| **Cap Space** | {cap_space} |
| **1st Apron Space** | {first_apron_space} |
| **2nd Apron Space** | {second_apron_space} |
"""

    # Exception Table
    exceptions_md = """\
|     |     |     |     |
| --- | --- | --- | --- |
| **Free Agency Ex­cep­tions** | **Avail­able?** | **Remaining** | **Triggers Hard Cap?** |
""" + "\n".join(
        f"| **{label}** | {data['available']} | {data['amount']} | {data['trigger']} |"
        for label, data in exceptions.items()
    )

    # TPE Table
    tpe_md = """\
|     |     |
| --- | --- |
| **Trad­ed Play­er Ex­cep­tions** | **Amount** |
""" + (
        "\n".join(f"| {tpe['player']} | {format_dollar(tpe['amount'])} |" for tpe in tpes)
        if tpes else "| No TPEs available | – |"
    )

    return "\n\n".join([cap_summary_md, exceptions_md, tpe_md])
