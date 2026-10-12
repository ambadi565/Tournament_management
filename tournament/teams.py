"""Team management module for creating and querying franchise teams."""

import sqlite3
from typing import Optional
from db import get_conn
from decorators import login_required, admin_only, log_action, timer


# [Concept: Decorators] Stacked decorators on CLI create_team
@login_required
@admin_only
@log_action
@timer
def create_team() -> None:
    """Prompt CLI administrator to register a new franchise team."""
    print("\n--- Create New Team ---")
    name = input("Team Name: ").strip()
    owner = input("Owner Name: ").strip()
    try:
        purse = int(input("Purse Budget (e.g. 1000): ").strip())
        if purse <= 0:
            print("Error: Purse must be greater than zero.")
            return
        max_str = input("Max Players [default: 11]: ").strip()
        max_players = int(max_str) if max_str else 11
        if max_players <= 0:
            print("Error: Max players must be positive.")
            return
    except ValueError:
        print("Error: Purse and max players must be valid integers.")
        return

    if not name:
        print("Error: Team name cannot be empty.")
        return

    # [Concept: SQLite] Parameterized INSERT query
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO teams (name, owner, purse, max_players) VALUES (?, ?, ?, ?);",
            (name, owner, purse, max_players),
        )
        conn.commit()
        print(f"Success: Team '{name}' created with purse ${purse} and squad cap {max_players}.")
    except sqlite3.IntegrityError:
        conn.rollback()
        print(f"Error: Team with name '{name}' already exists.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()


def list_teams() -> list[tuple]:
    """Retrieve all teams from the database.

    Returns:
        list[tuple]: List of team tuples (id, name, owner, purse, max_players).
    """
    # [Concept: SQLite] SELECT * FROM teams
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, owner, purse, max_players FROM teams ORDER BY id;")
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def get_team(team_id: int) -> Optional[dict]:
    """Fetch details of a single franchise team by its identifier.

    Args:
        team_id: Primary key ID of the team.

    Returns:
        dict | None: Dictionary representation of the team or None.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, owner, purse, max_players FROM teams WHERE id = ?;", (team_id,))
        row = cursor.fetchone()
        if row is not None:
            return dict(row)
        return None
    finally:
        cursor.close()
        conn.close()


def create_team_web(name: str, owner: str, purse: int, max_players: int) -> bool:
    """Create a new team via web interface submission.

    Args:
        name: Team title.
        owner: Owner name.
        purse: Salary cap purse.
        max_players: Maximum roster size.

    Returns:
        bool: True if created, False on failure or UNIQUE constraint violation.
    """
    clean_name = name.strip()
    clean_owner = owner.strip()
    try:
        purse_val = int(purse)
        max_val = int(max_players) if max_players else 11
        if purse_val <= 0 or max_val <= 0 or not clean_name:
            return False
    except (ValueError, TypeError):
        return False

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO teams (name, owner, purse, max_players) VALUES (?, ?, ?, ?);",
            (clean_name, clean_owner, purse_val, max_val),
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
