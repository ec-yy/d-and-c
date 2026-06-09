# This module contains functions to undertake airport-related opeartions, including:
#   - add_new_airport           → Menu 2.1 (Add new airport)
#   - view_update_airport       → Menu 8 (View or update airport information)

from rule import record_exists, non_empty_input, valid_choice, valid_id_input 


# ── Functions ───────────────────────────────────────────────────────────────────

# Function to add a new airport
def add_new_airport(connection, cursor):
    print("\n<----- Add a New Airport ----->")

    # Provide an airport ID in a prescribed format (i.e., 3 uppercase letters).
    airport_id = valid_id_input("Please provide an airport ID (e.g. NRT): ", r"^[A-Z]{3}$", "e.g., NRT")
    if record_exists(cursor, "Airport", "airport_id", airport_id):
        print(f"Sorry. Airport (ID: {airport_id}) already exists in the table <Airport>. Go to <Main Menu → Option 8> to update individual airport record.")
        return

    # Provide an airport name, country and city. All of them must be non-empty strings.
    airport_name = non_empty_input("Enter airport name: ")
    country = non_empty_input("Enter country: ")
    city = non_empty_input("Enter city: ")

    # Try to add a new airport to the table <Airport> based on user input and catch any exception.
    try:
        cursor.execute("""
            INSERT INTO Airport (airport_id, airport_name, country, city)
            VALUES (?, ?, ?, ?)
        """, (airport_id, airport_name, country, city))
        connection.commit()
        print(f"Great! Airport {airport_id} is added to the table <Airport>.")
    except Exception as e:
        print("Sorry. Failure in operation <Add a new airport>: ", e)


# Function to view or update specific airport information
def view_update_airport(connection, cursor):
    print("\n<----- View or Update Airport ----->")

    # Provide an airport ID that conforms to a prescribed format (i.e., 3 uppercase letters).
    airport_id = valid_id_input("Please provide an airport ID (e.g. NRT): ", r"^[A-Z]{3}$", "e.g., NRT")

    # Fetch the airport record from table <Airport> based on airport ID provided by user.
    cursor.execute("""
        SELECT *
        FROM Airport
        WHERE airport_id = ?
    """, (airport_id,))
    row = cursor.fetchone()

    if not row:
        print(f"Sorry. Airport (ID: {airport_id}) is not found in the table <Airport>.")
        return

    print(f"\n<----- Current Airport Record ----->")
    print(f"  Airport ID : {airport_id}")
    print(f"  Name       : {row[1]}")
    print(f"  Country    : {row[2]}")
    print(f"  City       : {row[3]}")

    # Prompt users if they want to update the airport information.
    user_input = valid_choice(f"Do you want to update information of Airport (ID: {airport_id})? (Y/N): ", ["Y", "N"])
    if user_input == 'N':
        return

    print("Press <Enter> to keep the value in current field.")
    revised_name = input(f"New airport name (Old name: {row[1]}): ").strip()
    revised_country = input(f"New country (Old name: {row[2]}): ").strip()
    revised_city = input(f"New city (Old name: {row[3]}): ").strip()

    updated_name = revised_name if revised_name else row[1]
    updated_country = revised_country if revised_country else row[2]
    updated_city = revised_city if revised_city else row[3]

    # Try to update the airport record based on user input and catch any exception.
    try:
        cursor.execute("""
            UPDATE Airport
            SET airport_name = ?, country = ?, city = ?
            WHERE airport_id = ?
        """, (updated_name, updated_country, updated_city, airport_id))
        connection.commit()
        print(f"Great! Airport (ID: {airport_id}) is updated.")

    except Exception as e:
        print(f"Sorry. Database error when updating airport (ID: {airport_id}): {e}")