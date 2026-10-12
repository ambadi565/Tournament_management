"""Match fixture generation, scheduling, and match result reporting."""

import sqlite3
# [Concept: Modules] random and datetime modules
import random
from datetime import datetime, timedelta
from typing import Optional
from db import get_conn


# [Concept: datetime] now(), strftime(), timedelta for match scheduling
def generate_matches() -> None:
    """Generate round-robin match fixtures for all registered teams."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM teams ORDER BY id;")
        teams = cursor.fetchall()
        team_count = len(teams)
        if team_count < 2:
            print("Cannot generate fixtures: At least 2 teams are required.")
            return

        pairs: list[tuple[int, int]] = []
        # [Concept: Loops] Nested for loops generating all pairwise combinations
        for i in range(team_count):
            for j in range(i + 1, team_count):
                pairs.append((teams[i]["id"], teams[j]["id"]))

        # Shuffle fixture order randomly
        random.shuffle(pairs)

        # Clear existing unplayed fixtures or insert new round-robin schedule
        base_date = datetime.now()
        for idx, (t1, t2) in enumerate(pairs):
            match_date = (base_date + timedelta(days=idx + 1)).strftime("%Y-%m-%d %H:%M")
            # [Concept: SQLite] Parameterized INSERT query
            cursor.execute(
                "INSERT INTO matches (team1_id, team2_id, match_date, score1, score2, played) VALUES (?, ?, ?, 0, 0, 0);",
                (t1, t2, match_date),
            )
        conn.commit()
        print(f"Successfully generated {len(pairs)} round-robin fixtures.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error during fixture generation: {e}")
    finally:
        cursor.close()
        conn.close()


def list_matches() -> list[tuple]:
    """Retrieve all match fixtures joined with team franchise names.

    Returns:
        list[tuple]: List of match tuples (id, team1, team2, match_date, score1, score2, played).
    """
    # [Concept: SQLite] JOIN query between matches and teams tables
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT m.id, t1.name AS team1, t2.name AS team2, m.match_date, m.score1, m.score2, m.played
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.id
            JOIN teams t2 ON m.team2_id = t2.id
            ORDER BY m.id;
            """
        )
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def enter_result() -> None:
    """Prompt CLI administrator to record the outcome of an unplayed match fixture."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT m.id, t1.name AS team1, t2.name AS team2, m.match_date
            FROM matches m
            JOIN teams t1 ON m.team1_id = t1.id
            JOIN teams t2 ON m.team2_id = t2.id
            WHERE m.played = 0
            ORDER BY m.id;
            """
        )
        unplayed = cursor.fetchall()
        if not unplayed:
            print("No pending matches found to record results for.")
            return

        print("\n--- Unplayed Matches ---")
        for m in unplayed:
            print(f"[{m['id']}] {m['team1']} vs {m['team2']} ({m['match_date']})")

        try:
            match_id = int(input("\nEnter Match ID: ").strip())
            s1 = int(input("Enter Score for Team 1: ").strip())
            s2 = int(input("Enter Score for Team 2: ").strip())
        except ValueError:
            print("Invalid input. Scores and Match ID must be integers.")
            return

        cursor.execute(
            "UPDATE matches SET score1 = ?, score2 = ?, played = 1 WHERE id = ?;",
            (s1, s2, match_id),
        )
        conn.commit()
        print(f"Match {match_id} result saved: {s1} - {s2}.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error updating match: {e}")
    finally:
        cursor.close()
        conn.close()


def enter_result_web(match_id: int, s1: int, s2: int) -> None:
    """Record a match fixture score originating from the web frontend.

    Args:
        match_id: Target fixture ID.
        s1: Score of team 1.
        s2: Score of team 2.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # [Concept: SQLite] Parameterized UPDATE query
        cursor.execute(
            "UPDATE matches SET score1 = ?, score2 = ?, played = 1 WHERE id = ?;",
            (int(s1), int(s2), int(match_id)),
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
