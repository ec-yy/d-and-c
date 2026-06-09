# This module contains functions to undertake pilot-related opeartions, including:
#   - add_new_pilot              → Menu 2.3 (Add new pilot)
#   - view_pilot_schedule        → Menu 6 (View pilot schedule)
#   - assign_pilot_to_flight     → Menu 7 (Assign a pilot to a flight)

from rule import record_exists, non_empty_input, valid_choice, valid_id_input 


# ── Functions ───────────────────────────────────────────────────────────────────

# Function to add a new pilot
def add_new_pilot(connection, cursor):
    print("\n<----- Add New Pilot ----->")
    
    # Provide a pliot ID in a prescribed format (i.e., 1 uppercase letter followed by 3 digits).
    pilot_id = valid_id_input("Please provide pilot ID (e.g., P001): ", r"^[A-Z][0-9]{3}$", "e.g., P001")
    if record_exists(cursor, "Pilot", "pilot_id", pilot_id):
        print(f"Sorry. Pilot (ID: {pilot_id}) already exists in the table.")
        return

    # Provide aviation license ID, first name and last name of the pilot. All of them must be non-empty strings.
    # The license ID should conform to a prescribed format (i.e., 3 uppercase letter followed by 3 digits).
    while True:
        license_id = valid_id_input("Please provide license ID (e.g., PLI001): ", r"^[A-Z]{3}[0-9]{3}$", "e.g., PLI001")
        if not record_exists(cursor, "Pilot", "license_id", license_id):
            break
        print(f"Sorry. License ID (ID: {license_id}) already exists in the table. Please try again")
    first_name = non_empty_input("First name: ")
    last_name = non_empty_input("Last name: ")

    # Provide a rank of the pilot
    input_rank = valid_choice("What is the pilot's rank (Select 1 for Captain, 2 for First Officer): ", ["1", "2"])
    final_rank = "Captain" if input_rank == "1" else "First Officer"

    # Try to add a new pilot to the table <Pilot> based on user input and catch any exception.
    try:
        cursor.execute("""
            INSERT INTO Pilot (pilot_id, license_id, first_name, last_name, rank)
            VALUES (?, ?, ?, ?, ?)
        """, (pilot_id, license_id, first_name, last_name, final_rank))
        connection.commit()
        print(f"Great! Pilot (ID: {pilot_id}) is added to the table <Pilot>.")
    except Exception as e:
        print("Sorry. Failure in operation <Add a new pilot>: ", e)


# Function to view specific pilot schedule
def view_pilot_schedule(cursor):
    print("\n<----- View Pilot Schedule ----->")
    
    # Provide a pilot ID in a prescribed format (i.e., 1 uppercase letter followed by 3 digits).
    pilot_id = valid_id_input("Please provide Pilot ID (e.g., P001): ", r"^[A-Z][0-9]{3}$", "e.g., P001")

    if not record_exists(cursor, "Pilot", "pilot_id", pilot_id):
        print(f"Sorry. Pilot (ID: {pilot_id}) is not found in the table <Pilot>.")
        return

    cursor.execute("""
        SELECT flight.flight_id,
               route.route_id,
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
        WHERE flight.captain_pilot_id = ? OR flight.first_officer_pilot_id = ?
        ORDER BY flight.departure_date_time
    """, (pilot_id, pilot_id))

    rows = cursor.fetchall()

    if not rows:
        print(f"Sorry. Pilot (ID: {pilot_id}) has no scheduled flights.")
        return

    print(f"\n<----- Flight Schedule for Pilot (ID: {pilot_id}) (Number of records: {len(rows)}) ----->")
    print()
    print("{:<7} {:<6} {:<20} {:<19} {:<10} {:<13} {:<14} {:<14} {:<14} {}".format(
        "Flight", "Route", "Departure Date/Time", "Arrival Date/Time", "Duration", "Status",
        "From Country", "From City", "To Country", "To City"))
    print("-" * 135)
    for row in rows:
        print("{:<7} {:<6} {:<20} {:<19} {:<10} {:<13} {:<14} {:<14} {:<14} {}".format(
            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))


# Function to assign a pilot to a flight
def assign_pilot_to_flight(connection, cursor):
    print("\n<----- Pilot Assignment ----->")
    print("Note: Any pre-existing pilot assignment for the flight will be superseded by the new assignment.")
    
    flight_id = valid_id_input("Please provide flight ID (e.g., F001): ", r"^[A-Z][0-9]{3}$", "e.g., F001")
    if not record_exists(cursor, "Flight", "flight_id", flight_id):
        print(f"Sorry. Flight (ID: {flight_id}) is not found in the table <Flight>.")
        return
    
    pilot_id = valid_id_input("Please provide pilot ID (e.g., P001): ", r"^[A-Z][0-9]{3}$", "e.g., P001")
    cursor.execute("""
        SELECT rank
        FROM Pilot
        WHERE pilot_id = ?
    """, (pilot_id,))
    row = cursor.fetchone()
    if not row:
        print(f"Sorry. Pilot (ID: {pilot_id}) is not found in the table <Pilot>.")
        return  

    column = "captain_pilot_id" if row[0] == "Captain" else "first_officer_pilot_id"

    # Try to update the flight record with the new pilot assignment based on user input and catch any exception.
    # This assumes that any pre-existing pilot assignment for the flight will be superseded by your new assignment.
    try:
        cursor.execute(f"""
            UPDATE Flight
            SET {column} = ?
            WHERE flight_id = ?
        """, (pilot_id, flight_id))
        connection.commit()
        print(f"Great! Pilot (ID: {pilot_id}) is assigned to a flight (ID: {flight_id}).")
    
    except Exception as e:
        print(f"Sorry. Database error when assigning pilot (ID: {pilot_id}) to flight (ID: {flight_id}): {e}")