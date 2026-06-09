# This module contains functions to undertake flight-related operations, including:
#   - add_new_flight                → Menu 2.4 (Add new flight)
#   - flight_summary_by_destination → Menu 3.1 (Number of flight by each destination)
#   - flight_summary_by_pilot       → Menu 3.2 (Number of flight by each pilot)
#   - view_flights_by_criteria      → Menu 4   (View flights by criteria)
#   - update_flight_information     → Menu 5   (Update flight information)

from rule import record_exists, valid_pilot_rank, valid_choice, valid_id_input, valid_date_time_format, valid_date_format 


# ── Constants ────────────────────────────────────────────────────────────────

# This is for static mapping of numeric menu choice to status in string.
STATUS_MAP = {"1": "On Schedule", "2": "Delayed", "3": "Cancelled", "4": "Departed", "5": "Arrived"}


# ── Functions ───────────────────────────────────────────────────────────────────

# Function to enable pre-defined choices of flight status and prompt user keep the current value.
def _prompt_status(current=None):
    print("\n<----- Flight Status ----->")
    print(" Select status: ")
    print("  1: On Schedule")
    print("  2: Delayed")
    print("  3: Cancelled")
    print("  4: Departed")
    print("  5: Arrived")

    if current:
        # Allow blank input from user to keep current selection.
        while True:
            raw_input = input(f"Please choose 1-5 [Current choice: {current}] (Note: Press <Enter> to keep current selection): ").strip()
            if not raw_input:
                return current          # keep unchanged
            if raw_input in ("1", "2", "3", "4", "5"):
                return STATUS_MAP[raw_input]
            print("Sorry. Invalid input. Please only choose from 1-5.")
    else:
        raw_input = valid_choice("Please choose from 1-5: ", ["1", "2", "3", "4", "5"])
        return STATUS_MAP[raw_input]


# ── Core functions ────────────────────────────────────────────────────────────

# Function to add a new flight
def add_new_flight(connection, cursor):
    print("\n<----- Add a New Flight ----->")

    # Provide a flight ID in a prescribed format (i.e., 1 uppercase letter followed by 3 digits).
    flight_id = valid_id_input("Please provide a flight ID (e.g. F001): ", r"^[A-Z][0-9]{3}$", "e.g., F001")
    if record_exists(cursor, "Flight", "flight_id", flight_id):
        print(f"Sorry. Flight (ID: {flight_id}) already exists in the table <Flight>. Go to <Main Menu → Option 4> to update individual flight record.")
        return

    # Provide departure date and time in a valid format (i.e., YYYY-MM-DD HH:MM:SS).
    departure_date_time = valid_date_time_format("Enter departure date and time (YYYY-MM-DD HH:MM): ", mandatory_input=True)

    status = _prompt_status()

    # Provide a valid route ID that exists in the corresponding tables.
    while True:
        route_id = valid_id_input("Enter route ID (e.g. AY001): ", r"^[A-Z]{2}[0-9]{3}$", "e.g., AY001")
        if not record_exists(cursor, "Route", "route_id", route_id):
            print(f"Sorry. Route (ID: {route_id}) is not found in the table <Route>. Please try again.")
            continue
        break

    # Provide a captain pilot ID and first officer pilot ID that exist in the corresponding tables.
    # Ensure pilot is assigned to flight in accordance with their rank (i.e., Captain vs First Officer).
    while True:
        captain_id = valid_id_input("Enter Captain Pilot ID (e.g. P001): ", r"^[A-Z][0-9]{3}$", "e.g., P001")
        if not record_exists(cursor, "Pilot", "pilot_id", captain_id):
            print(f"Sorry. Captain (ID: {captain_id}) is not found in the table <Pilot>. Please try again.")
            continue
        if not valid_pilot_rank(cursor, captain_id, "Captain"):
            print(f"Sorry. Pilot (ID: {captain_id}) does not hold the rank of Captain. Please try again.")
            continue
        break

    while True:
        first_officer_id = valid_id_input("Enter First Officer Pilot ID (e.g, P001): ", r"^[A-Z][0-9]{3}$", "e.g., P001")
        if not record_exists(cursor, "Pilot", "pilot_id", first_officer_id):
            print(f"Sorry. First Officer (ID: {first_officer_id}) is not found in the table <Pilot>. Please try again.")
            continue
        if not valid_pilot_rank(cursor, first_officer_id, "First Officer"):
            print(f"Sorry. Pilot (ID: {first_officer_id}) does not hold the rank of First Officer. Please try again.")
            continue
        break

    # Try to add a new flight to the table <Flight> based on user input and catch any exception.    
    try:
        cursor.execute("""
            INSERT INTO Flight
                (flight_id, departure_date_time, status, route_id, captain_pilot_id, first_officer_pilot_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (flight_id, departure_date_time, status, route_id, captain_id, first_officer_id))
        connection.commit()
        print(f"Great! Flight (ID: {flight_id}) is added to the table <Flight>.")
    except Exception as e:
        print("Sorry. Failure in operation <Add a new flight>: ", e)


def flight_summary_by_destination(cursor):
    cursor.execute("""
        SELECT airport.country,
               airport.city,
               COUNT(*) AS flight_count
        FROM Flight flight
        JOIN Route route ON flight.route_id = route.route_id
        JOIN Airport airport ON route.destination_airport_id = airport.airport_id
        GROUP BY airport.airport_id
        ORDER BY flight_count DESC
    """)
    rows = cursor.fetchall()

    print(f"\n<----- Number of Flights by Destination (Number of records: {len(rows)})----->")
    if not rows:
        print("Sorry. No flight data is available.")
        return

    print("\n{:<22} {:<20} {}".format("Destination Country", "Destination City", "No. of Flights"))
    print("-" * 58)
    for row in rows:
        print("{:<22} {:<20} {}".format(row[0], row[1], row[2]))


def flight_summary_by_pilot(cursor):
    cursor.execute("""
        SELECT pilot.pilot_id,
               pilot.first_name || ' ' || pilot.last_name AS full_name,
               pilot.rank,
               COUNT(*) AS flight_count
        FROM Pilot pilot
        JOIN Flight flight
          ON pilot.pilot_id = flight.captain_pilot_id
          OR pilot.pilot_id = flight.first_officer_pilot_id
        GROUP BY pilot.pilot_id
        ORDER BY flight_count DESC
    """)
    rows = cursor.fetchall()

    print(f"\n<----- Flight Summary by Pilot (Number of records: {len(rows)}) ----->")
    if not rows:
        print("Sorry. No pilot assignment data is available.")
        return

    print("\n{:<10} {:<28} {:<18} {}".format(
        "Pilot ID", "Full Name", "Rank", "Flights"))
    print("-" * 65)
    for row in rows:
        print("{:<10} {:<28} {:<18} {}".format(
            row[0], row[1], row[2], row[3]))


# Function to view flights by user-defined criteria
def view_flights_by_criteria(cursor):
    print("\n<----- View Flights by Criteria ----->")

    # Departure date filter — required only if the user wants to filter by departure date.
    # <valid_choice> is configured to ensure input is either "Y" or "N".
    departure_date = None
    if valid_choice("Do you want to apply filter by departure date? (Y/N): ", ["Y", "N"]) == "Y":
        departure_date = valid_date_format("Date of Departure (Input Format: YYYY-MM-DD) (Note: You can still press <Enter> to skip): ", mandatory_input=False)

    # Status filter — required only if the user wants to filter by status.
    status_filter = None
    if valid_choice("Do you want to apply filter by flight status? (Y/N): ", ["Y", "N"]) == "Y":
        status_filter = _prompt_status()

    # Destination filter - user can press <Enter> to skip either of them.
    destination_country = input("Destination country (Press <Enter> to skip): ").strip()
    destination_city = input("Destination city (Press <Enter> to skip): ").strip()

    parameter = []
    query = """
        SELECT flight.flight_id,
               flight.departure_date_time,
               strftime('%Y-%m-%d %H:%M', datetime(flight.departure_date_time, '+' || route.duration_minutes || ' minutes')) AS arrival_date_time,
               printf('%02d', route.duration_minutes / 60) || ':' || printf('%02d', route.duration_minutes % 60) AS duration_hours_minutes,
               flight.status,
               origin_airport.country AS from_country,
               origin_airport.city AS from_city,
               destination_airport.country AS to_country,
               destination_airport.city AS to_city
        FROM Flight flight
        JOIN Route route ON flight.route_id = route.route_id
        JOIN Airport origin_airport ON route.origin_airport_id = origin_airport.airport_id
        JOIN Airport destination_airport ON route.destination_airport_id = destination_airport.airport_id
        WHERE 1 = 1
    """

    if departure_date:
        query += " AND flight.departure_date_time LIKE ?"
        parameter.append(f"{departure_date}%")

    if status_filter:
        query += " AND flight.status = ?"
        parameter.append(status_filter)

    if destination_country:
        query += " AND destination_airport.country LIKE ?"
        parameter.append(f"%{destination_country}%")

    if destination_city:
        query += " AND destination_airport.city LIKE ?"
        parameter.append(f"%{destination_city}%")

    query += " ORDER BY flight.departure_date_time"

    cursor.execute(query, parameter)
    rows = cursor.fetchall()

    if not rows:
        print("\nSorry. No flights are found for these criteria.")
        return
    
    print(f"\n<----- Flight Schedule (Number of records: {len(rows)}) ----->")   
    print("\n{:<6} {:<21} {:<19} {:<10} {:<13} {:<14} {:<14} {:<14} {}".format(
        "Flight", "Departure Date/Time", "Arrival Date/Time", "Duration", "Status", "From Country", "From City", "To Country", "To City"))
    print("-" * 130)
    for row in rows:
        print("{:<6} {:<21} {:<19} {:<10} {:<13} {:<14} {:<14} {:<14} {}".format(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

# Function to update flight information (departure datetime and status)
def update_flight_information(connection, cursor):
    print("\n<----- Update Flight Information ----->")

    # Provide a flight ID in a prescribed format (i.e., 1 uppercase letter followed by 3 digits).    
    flight_id = valid_id_input("Enter Flight ID (e.g. F001): ", r"^[A-Z][0-9]{3}$", "e.g., F001")

    cursor.execute("""
        SELECT flight_id, departure_date_time, status
        FROM Flight
        WHERE flight_id = ?
    """, (flight_id,))
    row = cursor.fetchone()

    if not row:
        print(f"Sorry. Flight {flight_id} is not found in the table <Flight>.")
        return

    print(f"\n<----- Current Flight Record ----->")
    print(f"  Flight ID                : {row[0]}")
    print(f"  Departure Date and Time  : {row[1]}")
    print(f"  Status                   : {row[2]}")

    # Prompt users if they want to update the flight information.
    user_input = valid_choice(f"Do you want to update information of Flight (ID: {flight_id})? (Y/N): ", ["Y", "N"])
    if user_input == 'N':
        return

    print("Press <Enter> to keep the value in current field.")
    prompt = f"New departure date and time [{row[1]}] (Input Format: YYYY-MM-DD HH:MM:SS, or leave empty to skip): "
    # mandatory_input=False allows empty input to keep skip
    raw_input = valid_date_time_format(prompt, mandatory_input=False)  
    updated_departure_date_time = raw_input if raw_input else row[1]

    # Use function <_prompt_status> to either keep current selection or choose a new status from pre-defined options.
    updated_status = _prompt_status(current=row[2])

    try:
        cursor.execute("""
            UPDATE Flight
            SET departure_date_time = ?, status = ?
            WHERE flight_id = ?
        """, (updated_departure_date_time, updated_status, flight_id))
        connection.commit()
        print(f"Great! Flight (ID: {flight_id}) is updated.")

    except Exception as e:
        print(f"Sorry. Database error when updating flight (ID: {flight_id}): {e}")