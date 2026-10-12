"""Data export and recursive hierarchical report generation module."""

# [Concept: Modules] json, csv, os modules for data serialization and filesystem operations
import json
import csv
import os
import sqlite3
from typing import Any
from db import get_conn
from standings import show_points_table


# [Concept: Recursion] recursive_report() walks teams -> players hierarchically
def recursive_report(items: list[Any], depth: int = 0) -> None:
    """Recursively print hierarchical tournament structures (teams and member players).

    Args:
        items: List of dictionaries or nested lists representing tournament entities.
        depth: Current recursion depth level for indentation.
    """
    indent = "  " * depth
    for item in items:
        if isinstance(item, dict):
            name = item.get("name", "Unknown")
            entity_type = item.get("type", "Entity")
            print(f"{indent}- [{entity_type}] {name}")
            children = item.get("children", [])
            if children:
                # Recursive step down to child nodes (e.g. team -> players)
                recursive_report(children, depth + 1)
        elif isinstance(item, (list, tuple)):
            print(f"{indent}- Item: {item}")


# [Concept: File handling] JSON export (json.dump) with open(...)
def export_json() -> None:
    """Export complete tournament state to report.json in structured JSON format."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, owner, purse, max_players FROM teams;")
        teams = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, name, role, base_price, sold_to, price FROM players;")
        players = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, team1_id, team2_id, match_date, score1, score2, played FROM matches;")
        matches = [dict(r) for r in cursor.fetchall()]

        points = show_points_table()
        points_data = [
            {"team": p[0], "played": p[1], "won": p[2], "drawn": p[3], "points": p[4]}
            for p in points
        ]

        data = {
            "teams": teams,
            "players": players,
            "matches": matches,
            "points_table": points_data,
        }

        # Write to report.json in current directory and local tournament folder
        paths = ["report.json"]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(base_dir, "report.json")
        if alt_path not in paths:
            paths.append(alt_path)

        for path in paths:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        print("JSON report successfully exported to report.json")
    finally:
        cursor.close()
        conn.close()


# [Concept: File handling] CSV export (csv.writer) with open(...)
def export_csv() -> None:
    """Export the tournament league standings to points.csv in tabular CSV format."""
    points = show_points_table()
    paths = ["points.csv"]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    alt_path = os.path.join(base_dir, "points.csv")
    if alt_path not in paths:
        paths.append(alt_path)

    for path in paths:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Team", "Played", "Won", "Drawn", "Points"])
            for row in points:
                writer.writerow(row)

    print("Standings successfully exported to points.csv")
