"""Authentication and user management module for Tournament Management System."""

import sqlite3
from typing import Optional
from db import get_conn

# [Concept: Basic I/O, variables, constants, scope] Global variable current_user tracking session state
current_user: dict[str, Optional[str]] = {"name": None, "role": None}


def check_login(username: str, password: str) -> Optional[dict[str, str]]:
    """Verify user credentials against the database.

    Args:
        username: The account username.
        password: The account plaintext password.

    Returns:
        dict[str, str] | None: User info dictionary if valid, None otherwise.
    """
    # [Concept: SQLite] Parameterized SELECT query avoiding SQL injection
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT username, role FROM users WHERE username = ? AND password = ?;",
            (username, password),
        )
        row = cursor.fetchone()
        if row is not None:
            return {"username": row["username"], "role": row["role"]}
        return None
    finally:
        cursor.close()
        conn.close()


def create_user(username: str, password: str, role: str) -> bool:
    """Create a new user in the database.

    Args:
        username: The desired username.
        password: The desired password.
        role: User role, must be 'admin' or 'owner'.

    Returns:
        bool: True if created successfully, False on validation or database error.
    """
    # [Concept: Control] if/elif/else conditional validation
    clean_role = role.strip().lower()
    if clean_role not in ("admin", "owner"):
        return False
    if not username.strip() or not password.strip():
        return False

    conn = get_conn()
    cursor = conn.cursor()
    try:
        # [Concept: SQLite] Parameterized INSERT query
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?);",
            (username.strip(), password.strip(), clean_role),
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def register() -> None:
    """Interactive CLI user registration flow."""
    # [Concept: Basic I/O, variables, constants, scope] CLI input/output interactions
    print("\n--- User Registration ---")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    role = input("Enter role (admin/owner) [default: owner]: ").strip().lower() or "owner"

    if create_user(username, password, role):
        print(f"Success: User '{username}' registered as '{role}'.")
    else:
        print("Error: Could not register user. Username may already exist or input was invalid.")


def login() -> None:
    """Interactive CLI user login flow updating global current_user."""
    global current_user
    print("\n--- User Login ---")
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    user_data = check_login(username, password)
    # [Concept: Control] if/else branch handling login success
    if user_data is not None:
        current_user["name"] = user_data["username"]
        current_user["role"] = user_data["role"]
        print(f"Login successful! Welcome, {current_user['name']} ({current_user['role']}).")
    else:
        print("Error: Invalid username or password.")
