import re


def parse_salary_input(salary_input):
    # Remove $ sign and commas, make lowercase
    salary_input = salary_input.lower().replace('$', '').replace(',', '').strip()

    # Match formats like "240m", "240 million", "240mil", etc.
    million_match = re.match(r'^(\d+(\.\d+)?)(\s*)(m|mil|million)(\s*dollars*)?$', salary_input)
    if million_match:
        number = float(million_match.group(1))
        return number * 1_000_000

    # Match plain number like "240000000"
    number_match = re.match(r'^\d+(\.\d+)?$', salary_input)
    if number_match:
        return float(salary_input)

    # Try to catch phrases like "240 million dollars" with extra spaces
    words = salary_input.split()
    if len(words) >= 2 and words[1].startswith("mil"):
        try:
            return float(words[0]) * 1_000_000
        except ValueError:
            pass

    raise ValueError("Unrecognized salary format.")


def calculate_salary_per_year():
    try:
        salary_input = input("Enter total salary amount: ")
        total_salary = parse_salary_input(salary_input)

        years = float(input("Enter number of years: "))
        if years <= 0:
            print("Number of years must be greater than 0.")
            return

        salary_per_year = total_salary / years
        print(f"Salary per year: ${salary_per_year:,.2f}")

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    calculate_salary_per_year()
