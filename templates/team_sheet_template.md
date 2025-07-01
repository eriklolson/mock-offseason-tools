# {{team_name}} Cap Sheet

## Cap Summary
  | Category             | Value                |
  |----------------------|----------------------|
  | **Salary for Cap**   | {{salary_for_cap}}   |
  | **Cap Space**        | {{cap_space}}        |
  | **Luxury Tax space** | {{luxury_tax_space}} |
  | **1st Apron Room**   | {{apron1_space}}     |
  | **2nd Apron Room**   | {{apron2_space}}     |

---

## Free Agency Exceptions

  | Exception                    | Available (Y/N)          | Remaining Amount               | Triggers Hard Cap? |
  |------------------------------|--------------------------|--------------------------------|---------------------|
  | Cap Room Exception           | {{room_exception_yesno}} | {{room_exception_rem}}         | No                  |
  | Bi-Annual Exception (BAE)    | {{bae_yesno}}            | {{bae_exception_rem}}          | At 1st Apron        |
  | Taxpayer MLE                 | {{tp_mle_yesno}}         | {{tp_mle_rem}}                 | At 2nd Apron        |
  | Full MLE                     | {{full_mle_yesno}}       | {{full_mle_rem}}               | At 1st Apron        |

---

## Traded Player Exceptions

| Player           | Amount        |
|------------------|----------------|
| {{tpe_player1}}  | {{tpe_amt1}}   |
| {{tpe_player2}}  | {{tpe_amt2}}   |
| {{tpe_player3}}  | {{tpe_amt3}}   |

---

## Payroll

{{PLAYER_SALARY_TABLE}}

---

*Legend: 🔴 = AP Hold, 🔵 = Team Option, ⚪ = Non-Guaranteed, 🟢 = Player Option*
