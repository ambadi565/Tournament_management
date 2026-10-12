"""Database seeder populating initial demo accounts, teams, and players."""

import sys
import os
import sqlite3

# Ensure local tournament directory is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_conn, init_db


def seed_data() -> None:
    """Populate initial seed users, teams, and players into the database."""
    init_db()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # Seed users (admin and owner)
        users_data = [
            ("admin", "admin", "admin"),
            ("owner", "owner", "owner"),
        ]
        for u in users_data:
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?);",
                u,
            )

        # Seed 3 teams with purses (1000, 900, 800)
        teams_data = [
            ("Titan Warriors", "Titan Corp", 1000, 11),
            ("Royal Strikers", "Royal Club", 900, 11),
            ("Blaze Dynamos", "Blaze Ventures", 800, 11),
        ]
        for t in teams_data:
            cursor.execute(
                "INSERT OR IGNORE INTO teams (name, owner, purse, max_players) VALUES (?, ?, ?, ?);",
                t,
            )

        # Seed 8 players across various roles with base prices
        players_data = [
            ("Alex Mercer", "Batsman", 60),
            ("Marcus Sterling", "Bowler", 50),
            ("Jordan Vance", "All-Rounder", 75),
            ("Liam O'Connor", "Wicket-Keeper", 45),
            ("Devon Harris", "Batsman", 55),
            ("Ravi Patel", "Bowler", 50),
            ("Elena Rostova", "All-Rounder", 80),
            ("Samir Khan", "Batsman", 40),
        ]
        # Only seed players if table is empty
        cursor.execute("SELECT COUNT(*) AS c FROM players;")
        count = cursor.fetchone()["c"]
        if count == 0:
            for p in players_data:
                cursor.execute(
                    "INSERT INTO players (name, role, base_price) VALUES (?, ?, ?);",
                    p,
                )

        conn.commit()
        print("Seeded. Run: python main.py  or  python app.py")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    seed_data()
