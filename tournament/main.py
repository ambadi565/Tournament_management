"""Command-line interface entry point for Tournament Management System."""

import sys
import os

# Ensure local tournament directory is on path for relative execution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db
from auth import login, register, current_user
from players import add_player, list_players
from teams import create_team, list_teams
from auction import start_auction
from matches import generate_matches, enter_result, list_matches
from standings import show_points_table
from reports import export_json, export_csv, recursive_report


def display_menu() -> None:
    """Print the interactive command-line menu options."""
    user_badge = f"{current_user.get('name') or 'Guest'} ({current_user.get('role') or 'Not logged in'})"
    print("\n" + "=" * 50)
    print(f"🏆 TOURNAMENT MANAGEMENT SYSTEM [User: {user_badge}]")
    print("=" * 50)
    print(" 1. Login")
    print(" 2. Register")
    print(" 3. Add Player (Admin)")
    print(" 4. Add Team (Admin)")
    print(" 5. Live Player Auction")
    print(" 6. View Teams & Squads")
    print(" 7. Generate Fixtures / View Fixtures")
    print(" 8. Enter Match Result")
    print(" 9. Points Table & Standings")
    print("10. Export Reports (JSON & CSV)")
    print(" 0. Exit")
    print("=" * 50)


def main() -> None:
    """Initialize database and run interactive CLI event loop."""
    # Initialize the database schema upon launch
    init_db()

    # [Concept: Loops] while True loop for CLI session
    while True:
        display_menu()
        try:
            choice = input("Select an option (0-10): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting. Goodbye!")
            # [Concept: Transfer] break on exit signal
            break

        # [Concept: match-case] Python 3.10+ pattern matching on command menu input
        match choice:
            case "1":
                login()
            case "2":
                register()
            case "3":
                add_player()
            case "4":
                create_team()
            case "5":
                start_auction()
            case "6":
                teams = list_teams()
                if not teams:
                    print("No teams registered yet.")
                else:
                    print("\n--- Registered Teams ---")
                    for t in teams:
                        print(f"[{t[0]}] {t[1]} | Owner: {t[2]} | Purse: ${t[3]} | Cap: {t[4]}")
            case "7":
                print("\n1. View Fixtures\n2. Generate Round-Robin Fixtures (Admin)")
                sub = input("Select option: ").strip()
                if sub == "2":
                    generate_matches()
                else:
                    fixtures = list_matches()
                    if not fixtures:
                        print("No fixtures scheduled.")
                    else:
                        print("\n--- Tournament Fixtures ---")
                        for m in fixtures:
                            status = f"{m[4]} - {m[5]}" if m[6] else "Upcoming"
                            print(f"[{m[0]}] {m[1]} vs {m[2]} on {m[3]} | Status: {status}")
            case "8":
                enter_result()
            case "9":
                table = show_points_table()
                print("\n" + "=" * 45)
                print(f"{'Team':<15}{'P':<6}{'W':<6}{'D':<6}{'Pts':<6}")
                print("=" * 45)
                if not table:
                    print("No completed matches recorded.")
                else:
                    for row in table:
                        print(f"{row[0]:<15}{row[1]:<6}{row[2]:<6}{row[3]:<6}{row[4]:<6}")
                print("=" * 45)
            case "10":
                export_json()
                export_csv()
            case "0":
                print("Thank you for using Tournament Management System. Goodbye!")
                break
            case _:
                print("Invalid selection. Please choose an option from 0 to 10.")


if __name__ == "__main__":
    main()
