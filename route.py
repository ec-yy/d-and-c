# This module defines functions to undertake route-related operations, including:
#   - add_new_route              → Menu 2.2 (Add new route)

from rule import record_exists, positive_integer_input, valid_id_input


# ── Functions ───────────────────────────────────────────────────────────────────

# Function to add a new route.  
def add_new_route(connection, cursor):
    print("\n<----- Add New Route ----->")
    
    # Provide a route ID in a prescribed format (i.e., 2 uppercase letters followed by 3 digits).
    route_id = valid_id_input("Please provide a route ID (e.g. AY001): ", r"^[A-Z]{2}[0-9]{3}$", "e.g., AY001")
    if record_exists(cursor, "Route", "route_id", route_id):
        print(f"Sorry. Route (ID: {route_id}) already exists in the table <Route>.")
        return

    # Provide a duration (measured in minutes) that is a positive integer.
    duration = positive_integer_input("Please provide duration (in minutes): ")

    # Provide origin and destination airports
    # They both conform to a prescribed format (i.e., 3 uppercase letters) and must be different from each other.
    origin, destination = None, None

    while True:
        if origin is None:
            origin_input = valid_id_input("Enter Origin Airport ID (e.g., NRT): ", r"^[A-Z]{3}$", "e.g., NRT")
            if not record_exists(cursor, "Airport", "airport_id", origin_input):
                print(f"Sorry. Origin airport (ID: {origin_input}) not found and not supported by our airline. Please try again.")
                continue
            origin = origin_input

        if destination is None:
            destination_input = valid_id_input("Enter Destination Airport ID (e.g., LHR): ", r"^[A-Z]{3}$", "e.g., LHR")
            if not record_exists(cursor, "Airport", "airport_id", destination_input):
                print(f"Sorry. Destination airport (ID: {destination_input}) not found and not supported by our airline. Please try again.")
                continue
            destination = destination_input

        if origin == destination:
            print("Sorry. Origin and destination cannot be the same airport. Please try again.")
            origin, destination = None, None
            continue

        break

    print(f"Great! Origin and destination are validated. The route from {origin} to {destination} will be adopted.")

    # Try to add a new route to the table <Route> based on user input and catch any exception.
    try:
        cursor.execute("""
            INSERT INTO Route (route_id, duration_minutes, origin_airport_id, destination_airport_id)
            VALUES (?, ?, ?, ?)
        """, (route_id, duration, origin, destination))
        connection.commit()
        print(f"Great! Route (ID: {route_id}) is added to the table <Route>.")
    
    except Exception as e:
        print("Sorry. Failure in operation <Add a new route>: ", e)