"""Database connection and initialization module for Tournament Management System."""

# [Concept: Modules] sqlite3 module for relational database management
import sqlite3
import os

DB_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tournament.db")


def get_conn() -> sqlite3.Connection:
    """Establish and return a SQLite database connection with row factory and foreign keys enabled.

    Returns:
        sqlite3.Connection: Active database connection.
    """
    # [Concept: SQLite] Connection creation and foreign key pragma
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize the frozen database schema by creating required tables if they do not exist."""
    # [Concept: SQLite] CREATE with PK/FK/NOT NULL/UNIQUE/CHECK, commit, cursor.close(), conn.close()
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK(role IN ('admin','owner')) DEFAULT 'owner'
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                owner TEXT,
                purse INTEGER NOT NULL CHECK(purse > 0),
                max_players INTEGER DEFAULT 11
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                base_price INTEGER NOT NULL CHECK(base_price > 0),
                sold_to INTEGER,
                price INTEGER DEFAULT 0,
                sold_at TEXT,
                FOREIGN KEY(sold_to) REFERENCES teams(id)
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_players (
                team_id INTEGER,
                player_id INTEGER,
                price INTEGER,
                FOREIGN KEY(team_id) REFERENCES teams(id),
                FOREIGN KEY(player_id) REFERENCES players(id)
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team1_id INTEGER,
                team2_id INTEGER,
                match_date TEXT,
                score1 INTEGER,
                score2 INTEGER,
                played INTEGER DEFAULT 0,
                FOREIGN KEY(team1_id) REFERENCES teams(id),
                FOREIGN KEY(team2_id) REFERENCES teams(id)
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                user TEXT,
                ts TEXT
            );
            """
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
