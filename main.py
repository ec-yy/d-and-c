# It is the main module, which serves as the entry point of the Flight Management Application.
# It is Python-based command-line interface (CLI) and allow users to interact through its main and sub menus.

import sqlite3
from database import connect_database, reset_database, establish_database
from rule import view_table
from airport import add_new_airport, view_update_airport
from route import add_new_route
from pilot import add_new_pilot, view_pilot_schedule, assign_pilot_to_flight
from flight import add_new_flight, flight_summary_by_destination, flight_summary_by_pilot, view_flights_by_criteria, update_flight_information 

# Functions for different menu views and navigation.
def menu_main():
    print("\n<===== Flight Management Application Main Menu =====>")
    print("1. All: View")
    print("2. All: Add")
    print("3. All: Summary reports")
    print("4. Flight: View flights by criteria")
    print("5. Flight: Update flight information")
    print("6. Pilot: View pilot schedule")
    print("7. Pilot: Assign pilot to flight")
    print("8. Airport: View or update airport information")
    print("0. Exit")

def sub_menu_view():
    print("\n<----- Sub Menu 1: View ----->")
    print("1. View All: Airports")
    print("2. View All: Routes")
    print("3. View All: Pilots")
    print("4. View All: Flights")
    print("0. Back")

def sub_menu_add():
    print("\n<----- Sub Menu 2: Add ----->")
    print("1. Add: Airport")
    print("2. Add: Route")
    print("3. Add: Pilot")
    print("4. Add: Flight")
    print("0. Back")

def sub_menu_summary():
    print("\n<----- Sub Menu 3: Summary Reports ----->    ")
    print("1. Number of Flights: Each destination")
    print("2. Number of Flights: Each pilot")
    print("0. Back")

def navigate_menu(connection, cursor):
    while True:
        menu_main()
        choice = input("Select an option: ").strip()

        if choice == "1":
            while True:
                sub_menu_view()
                sub_choice = input("Select an option: ").strip()
                if sub_choice == "1":
                    view_table(cursor, "Airport", order_by="airport_id")
                elif sub_choice == "2":
                    view_table(cursor, "Route", order_by="route_id")
                elif sub_choice == "3":
                    view_table(cursor, "Pilot", order_by="pilot_id")
                elif sub_choice == "4":
                    view_table(cursor, "Flight", order_by="departure_date_time")
                elif sub_choice == "0":
                    break
                else:
                    print("Sorry. Invalid input. Please try again.")

        elif choice == "2":
            while True:
                sub_menu_add()
                sub_choice = input("Select an option: ").strip()
                if sub_choice == "1":
                    add_new_airport(connection, cursor)
                elif sub_choice == "2":
                    add_new_route(connection, cursor)
                elif sub_choice == "3":
                    add_new_pilot(connection, cursor)
                elif sub_choice == "4":
                    add_new_flight(connection, cursor)
                elif sub_choice == "0":
                    break
                else:
                    print("Sorry. Invalid input. Please try again.")

        elif choice == "3":
            while True:
                sub_menu_summary()
                sub_choice = input("Select an option: ").strip()
                if sub_choice == "1":
                    flight_summary_by_destination(cursor)
                elif sub_choice == "2":
                    flight_summary_by_pilot(cursor)
                elif sub_choice == "0":
                    break
                else:
                    print("Sorry. Invalid input. Please try again.")

        elif choice == "4":
            view_flights_by_criteria(cursor)

        elif choice == "5":
            update_flight_information(connection, cursor)

        elif choice == "6":
            view_pilot_schedule(cursor)

        elif choice == "7":
            assign_pilot_to_flight(connection, cursor)

        elif choice == "8":
            view_update_airport(connection, cursor)

        elif choice == "0":
            print("Goodbye.")
            break

        else:
            print("Sorry. Invalid input. Please try again.")


# A function to run the main program
def main():
    # To avoid scenario where "finally" block attempts to close a connection that does not exist.
    connection = None 
    
    try:
    # Prompt user to decide whether to reset the database.
    # If yes, old database will be removed and a new database will be created.    
        reset = reset_database()
        connection, cursor = connect_database()

        if reset:
            establish_database(cursor)
            # Only commit when tables are created and default data is inserted.
            connection.commit()
            print("A new database has been initialized with default data.")
            
        print("Database ready.")
        navigate_menu(connection, cursor)
        
    # This can catch the re-thrown error when calling functions in database.py, and any other error that may occur in this fucntion.
    except sqlite3.Error as e:
         print(f"Application aborted due to an error: {e}")   

    finally: 
        try:
            if connection is not None:
                connection.close()

        except:
            pass


if __name__ == "__main__":
    main()