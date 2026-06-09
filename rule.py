# This module contains functions to handle business rules, user input validation common to all other modules, including:

# ────────     1. Business Rules     ────────
#   1.1 → record_exists              → Check if a record already exists in a table based on a given primary key value
#   1.2 → valid_table                → Check if a table name is valid
#   1.3 → valid_pilot_rank           → Check if pilot assignment is in accordance with the rank (i.e., Captain or First Officer)

# ──────── 2. User Input Validation  ────────
#   2.1 → non_empty_input            → Check if user input is not empty
#   2.2 → integer_input              → Check if user input is an integer type
#   2.3 → positive_integer_input     → Check if user input is a positive integer
#   2.4 → valid_choice               → Check if user input is from a list of valid choice
#   2.5 → valid_id_input             → Check if user input conforms to a prescribed format (e.g., 1 uppercase letter followed by 3 digits)
#   2.6 → valid_date_time_format     → Check if user input is in a valid date and time format (i.e., YYYY-MM-DD HH:MM:SS)
#   2.7 → valid_date_format          → Check if user input is in a valid date format (i.e., YYYY-MM-DD)

# ────────    3. Common Utilities    ────────
#   3.1 → view_table                 → View complete records of a table with optional ordering

import re
from datetime import datetime

# ── 1. Functions - Business Rules ────────────────────────────────────────────────────────────

def record_exists(cursor, table, column, value):  
    if not valid_table(table):
        return False
    
    query = f"SELECT 1 FROM {table} WHERE {column} = ?"
    cursor.execute(query, (value,))
    return cursor.fetchone() is not None

def valid_table(table):
    valid_tables = {"Airport", "Route", "Pilot", "Flight"}
    if not table in valid_tables:
        print(f"{table} is not valid.")
        return False
    return True

def valid_pilot_rank(cursor, pilot_id, expected_rank):
    """
    Checks that the given pilot holds the expected rank.
    - expected_rank: "Captain" or "First Officer"
    - Returns True if rank matches, False otherwise.
    """
    cursor.execute("SELECT rank FROM Pilot WHERE pilot_id = ?", (pilot_id,))
    row = cursor.fetchone()
    if row and row[0] == expected_rank:
        return True
    return False

# ── 2. Functions - User Input Validation ────────────────────────────────────────────────────────────

def non_empty_input(system_prompt):
    while True:
        user_input = input(system_prompt).strip()
        if user_input:
            return user_input
        print("User input must be non-empty. Try again.")

def integer_input(system_prompt):
    while True:
        user_input = input(system_prompt).strip()
        try:
            return int(user_input)
        except ValueError:
            print("Invalid input. User input must be an integer. Try again.")

def positive_integer_input(system_prompt):
    while True:
        user_input = input(system_prompt).strip()
        try:
            value = int(user_input)
            if value > 0:
                return value
            else:
                print("Invalid input. User input must be a positive integer. Try again.")
        except ValueError:
            print("Invalid input. User input must be an integer. Try again.")

def valid_choice(system_prompt, choice):
    hint = " / ".join(choice)
    while True:
        user_input = input(system_prompt).strip().upper()
        if user_input in choice:
            return user_input
        print(f"Sorry. Invalid input. User input must be from {hint} only. Try again.")

def valid_id_input(system_prompt, pattern, example):
    while True:
        user_input = input(system_prompt).strip().upper()

        if not user_input:
            print("User input must be non-empty. Try again.")
            continue

        if re.fullmatch(pattern, user_input):
            return user_input
        else:
            print(f"Invalid input. The input should conform to a prescribed format (e.g., {example}). Try again.")

def valid_date_time_format(system_prompt, mandatory_input):
    pattern = "%Y-%m-%d %H:%M"
    while True:
        if mandatory_input == True:
            user_input = non_empty_input(system_prompt)
        else:
            user_input = input(system_prompt).strip()
            if not user_input:
                return None
        try:
            parsed_input = datetime.strptime(user_input, pattern)
            return parsed_input.strftime(pattern)
        except ValueError:
            print("Sorry. The date and time format is invalid. Please use YYYY-MM-DD HH:MM (e.g. 2026-06-06 14:30). Try again.")

def valid_date_format(system_prompt, mandatory_input):
    pattern = "%Y-%m-%d"
    while True:
        if mandatory_input == True:
            user_input = non_empty_input(system_prompt)
        else:
            user_input = input(system_prompt).strip()
            if not user_input:
                return None
        try:
            parsed_input = datetime.strptime(user_input, pattern)
            return parsed_input.strftime(pattern)
        except ValueError:
            print("Sorry. The date format is invalid. Please use YYYY-MM-DD (e.g. 2026-06-06). Try again.")

# ── 3. Functions - Common Utilities ────────────────────────────────────────────────────────────

def view_table(cursor, table_name, columns="*", order_by=None):
    # Fetch complete records of a table.
    query = f"SELECT {columns} FROM {table_name}"
    if order_by:
        query = query + f" ORDER BY {order_by}"
    cursor.execute(query)
    rows = cursor.fetchall()

    print(f"\n<----- {table_name} Complete Records ----->")
    if not rows:
        print(f"No records were found in {table_name}.")
        return

    # Fetch and print column names.
    column_names = [col[0] for col in cursor.description]
    header = " , ".join(column_names)
    print("\n" + header)

    # Print rows if there are records in the table.
    for row in rows:
        print(row)
