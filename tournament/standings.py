"""Tournament league standings and statistical aggregations module."""

import sqlite3
from typing import Any
from db import get_conn


def show_points_table() -> list[tuple]:
    """Calculate and return the tournament standings table using aggregate SQL and lambda sorting.

    Returns:
        list[tuple]: List of standings rows (Team, Played, Won, Drawn, Points).
    """
    # [Concept: SQLite] JOIN, GROUP BY + HAVING + CASE WHEN aggregate query
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT t.name,
              COUNT(m.id) AS P,
              SUM(CASE WHEN (m.team1_id=t.id AND m.score1>m.score2)
                    OR (m.team2_id=t.id AND m.score2>m.score1) THEN 1 ELSE 0 END) AS W,
              SUM(CASE WHEN (m.team1_id=t.id OR m.team2_id=t.id) AND m.score1=m.score2
                  THEN 1 ELSE 0 END) AS D,
              SUM(CASE WHEN (m.team1_id=t.id AND m.score1>m.score2)
                    OR (m.team2_id=t.id AND m.score2>m.score1) THEN 3
                   WHEN m.score1=m.score2 THEN 1 ELSE 0 END) AS Pts
            FROM teams t
            LEFT JOIN matches m
              ON (m.team1_id=t.id OR m.team2_id=t.id) AND m.played=1
            GROUP BY t.id
            HAVING COUNT(m.id) > 0
            ORDER BY Pts DESC, W DESC, t.name;
            """
        )
        raw_rows = cursor.fetchall()
        # [Concept: Sequences] tuple rows and dict mappings
        rows: list[tuple] = [
            (
                r["name"],
                int(r["P"] or 0),
                int(r["W"] or 0),
                int(r["D"] or 0),
                int(r["Pts"] or 0),
            )
            for r in raw_rows
        ]
        # [Concept: Lambda] Re-sort rows in Python using lambda key function: (-Pts, -W, name)
        return sorted(rows, key=lambda r: (-r[4], -r[2], r[0]))
    finally:
        cursor.close()
        conn.close()


def get_stats() -> dict[str, int]:
    """Aggregate total counts of players, teams, and played matches across the tournament.

    Returns:
        dict[str, int]: Summary stats dictionary {"players": n, "teams": n, "matches_played": n}.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) AS total_players FROM players;")
        players_count = cursor.fetchone()["total_players"]

        cursor.execute("SELECT COUNT(*) AS total_teams FROM teams;")
        teams_count = cursor.fetchone()["total_teams"]

        cursor.execute("SELECT COUNT(*) AS played_count FROM matches WHERE played = 1;")
        played_count = cursor.fetchone()["played_count"]

        # [Concept: Sequences] dict representation of summary statistics
        return {
            "players": int(players_count or 0),
            "teams": int(teams_count or 0),
            "matches_played": int(played_count or 0),
        }
    finally:
        cursor.close()
        conn.close()
