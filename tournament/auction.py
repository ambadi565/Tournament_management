"""Player auction mechanics, bidding engine, and purse balance accounting."""

import sqlite3
from datetime import datetime
from typing import Any, Optional
from db import get_conn


# [Concept: *args and **kwargs] Arbitrary positional bids and keyword metadata
def log_bid(*bids: Any, **meta: Any) -> None:
    """Log bid history with arbitrary bids and metadata keyword arguments.

    Args:
        *bids: Variable sequence of bid amounts or descriptions.
        **meta: Key-value metadata such as player, auctioneer, or round.
    """
    meta_str = ", ".join(f"{k}={v}" for k, v in meta.items())
    # [Concept: Loops] for loop iterating bids
    for bid in bids:
        print(f"[AUCTION AUDIT] Bid: ${bid} | Metadata: ({meta_str})")


def next_unsold() -> Optional[dict]:
    """Retrieve the next unsold player available for auction bidding.

    Returns:
        dict | None: Dictionary of player fields or None if all are sold.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name, role, base_price FROM players WHERE sold_to IS NULL ORDER BY id LIMIT 1;")
        row = cursor.fetchone()
        if row is not None:
            return dict(row)
        return None
    finally:
        cursor.close()
        conn.close()


def sell_player(player_id: int, team_id: int, price: int) -> bool:
    """Validate purse budget and squad capacity, then atomically assign player to team.

    Args:
        player_id: ID of the player being sold.
        team_id: Purchasing franchise team ID.
        price: Agreed sale price.

    Returns:
        bool: True if purchase succeeded, False otherwise.
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # [Concept: Control] Nested if control structure checking player eligibility
        cursor.execute("SELECT id, name, base_price, sold_to FROM players WHERE id = ?;", (player_id,))
        player_row = cursor.fetchone()
        if player_row is None:
            return False
        # [Concept: Operators] Identity (is not None) and relational (price < base_price)
        if player_row["sold_to"] is not None:
            return False
        if price < player_row["base_price"]:
            return False

        # Validate team constraints
        cursor.execute("SELECT id, name, purse, max_players FROM teams WHERE id = ?;", (team_id,))
        team_row = cursor.fetchone()
        if team_row is None:
            return False

        # [Concept: Operators] Relational check on team purse
        if team_row["purse"] < price:
            return False

        # Check roster capacity
        cursor.execute("SELECT COUNT(*) AS squad_count FROM team_players WHERE team_id = ?;", (team_id,))
        count_row = cursor.fetchone()
        squad_count = count_row["squad_count"] if count_row else 0
        if squad_count >= team_row["max_players"]:
            return False

        # Transaction execution: insert team_player, update player, deduct purse
        sold_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO team_players (team_id, player_id, price) VALUES (?, ?, ?);",
            (team_id, player_id, price),
        )
        cursor.execute(
            "UPDATE players SET sold_to = ?, price = ?, sold_at = ? WHERE id = ?;",
            (team_id, price, sold_at, player_id),
        )
        # [Concept: Operators] Arithmetic deduction
        cursor.execute(
            "UPDATE teams SET purse = purse - ? WHERE id = ?;",
            (price, team_id),
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def place_bid(player_id: int, team_id: int, amount: int) -> tuple[bool, str]:
    """Process a bid submission from the web interface.

    Args:
        player_id: Target player.
        team_id: Bidding team.
        amount: Bid price.

    Returns:
        tuple[bool, str]: Success boolean and descriptive status message.
    """
    try:
        p_id = int(player_id)
        t_id = int(team_id)
        bid_val = int(amount)
    except (ValueError, TypeError):
        return False, "Invalid bid parameters."

    success = sell_player(p_id, t_id, bid_val)
    if success:
        log_bid(bid_val, player_id=p_id, team_id=t_id, status="ACCEPTED")
        return True, f"Bid accepted! Player {p_id} sold to Team {t_id} for ${bid_val}."
    return False, "Bid rejected: Insufficient team purse, roster full, or player already sold."


def recent_bids(limit: int = 10) -> list[tuple]:
    """Retrieve the most recent player auction sales.

    Args:
        limit: Maximum records to return.

    Returns:
        list[tuple]: List of (player_id, player_name, team_name, price, sold_at).
    """
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT p.id, p.name, t.name AS team_name, p.price, p.sold_at
            FROM players p
            JOIN teams t ON p.sold_to = t.id
            ORDER BY p.id DESC
            LIMIT ?;
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [tuple(row) for row in rows]
    finally:
        cursor.close()
        conn.close()


def start_auction() -> None:
    """Run an interactive CLI player auction round."""
    # [Concept: Loops] while True loop with break and continue
    print("\n=== Live Player Auction ===")
    while True:
        player = next_unsold()
        if player is None:
            print("No more unsold players available for auction.")
            # [Concept: Transfer] break transfer statement
            break

        print(f"\nUp for Auction: [{player['id']}] {player['name']} ({player['role']}) — Base Price: ${player['base_price']}")
        choice = input("Enter 'b' to bid, 's' to skip to next menu, 'q' to quit auction: ").strip().lower()

        if choice == "q":
            break
        elif choice == "s":
            # [Concept: Transfer] continue transfer statement
            continue
        elif choice == "b":
            try:
                team_id = int(input("Enter Bidding Team ID: ").strip())
                bid_amount = int(input(f"Enter Bid Amount (>= ${player['base_price']}): ").strip())
            except ValueError:
                print("Invalid input. Please enter valid integer numbers.")
                continue

            success = sell_player(player["id"], team_id, bid_amount)
            if success:
                log_bid(bid_amount, player=player["name"], team_id=team_id)
                print(f"HAMMER DOWN! {player['name']} sold to Team {team_id} for ${bid_amount}!")
            else:
                print("Bid rejected: Check team purse, squad limit, or bid amount.")
        else:
            # [Concept: Transfer] pass statement
            pass
