"""Player management module with CLI and Web operations."""

import sqlite3
from typing import Optional
from db import get_conn
from decorators import login_required, admin_only, log_action, timer


# [Concept: Decorators] Stacked decorators on CLI add_player
@login_required
@admin_only
@log_action
@timer
def add_player() -> None:
    """Prompt CLI administrator to register a new player into the database."""
    print("\n--- Add New Player ---")
    name = input("Player Name: ").strip()
    role = input("Role (Batsman/Bowler/All-Rounder/Wicket-Keeper): ").strip().title()
    try:
        base_price = int(input("Base Price (e.g. 50): ").strip())
        if base_price <= 0:
            print("Error: Base price must be greater than zero.")
            return
    except ValueError:
        print("Error: Invalid numeric base price.")
        return

    if not name or not role:
        print("Error: Name and role cannot be empty.")
        return

    # [Concept: SQLite] Parameterized INSERT query
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO players (name, role, base_price) VALUES (?, ?, ?);",
            (name, role, base_price),
        )
        conn.commit()
        print(f"Success: Added player '{name}' ({role}) with base price ${base_price}.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error adding player: {e}")
    finally:
        cursor.close()
        conn.close()


def list_players() -> list[tuple]:
    """Fetch all player records with their associated franchise team names.

    Returns:
        list[tuple]: List of player tuples (id, name, role, base_price, team_name, price, sold_at).
    """
    # [Concept: SQLite] SELECT with LEFT JOIN
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT p.id, p.name, p.role, p.base_price, t.name AS team_name, p.price, p.sold_at
            FROM players p
            LEFT JOIN teams t ON p.sold_to = t.id
            ORDER BY p.id;
            """
        )
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def add_player_web(name: str, role: str, base_price: int) -> bool:
    """Insert a new player record originating from a web request.

    Args:
        name: Player full name.
        role: Player position or role.
        base_price: Starting auction price.

    Returns:
        bool: True on success, False on validation failure or database error.
    """
    clean_name = name.strip()
    clean_role = role.strip().title()
    try:
        price_val = int(base_price)
        if price_val <= 0 or not clean_name or not clean_role:
            return False
    except (ValueError, TypeError):
        return False

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO players (name, role, base_price) VALUES (?, ?, ?);",
            (clean_name, clean_role, price_val),
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
