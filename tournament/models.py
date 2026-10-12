"""Domain models and object-oriented relationship definitions for Tournament Management."""

# [Concept: Sequences] list for team squad and tournament matches
# [Concept: OOP] Classes Player, Team, Match, Tournament with __init__ + methods
from typing import Optional, Union


class Player:
    """Represents a tournament athlete available for recruitment and auction.

    Demonstrates a basic entity participating in relationships.
    """

    def __init__(self, name: str, role: str, base_price: int) -> None:
        """Initialize a Player instance.

        Args:
            name: Full name of the player.
            role: Playing role (e.g., Batsman, Bowler, All-Rounder, Wicket-Keeper).
            base_price: Starting auction bid price.
        """
        self.name: str = name
        self.role: str = role
        self.base_price: int = base_price
        self.sold_to: Optional[int] = None
        self.price: int = 0

    def __str__(self) -> str:
        """Return human-readable player representation."""
        return f"Player(name='{self.name}', role='{self.role}', base_price={self.base_price})"


class Team:
    """Represents a competing franchise in the tournament.

    Demonstrates AGGREGATION: Team 'has-a' collection of Player objects.
    Players exist independently of teams and can belong to no team or transfer.
    """

    # [Concept: Relationships] Aggregation — Team has-a Player (weak ownership)
    def __init__(self, name: str, owner: str, purse: int, max_players: int = 11) -> None:
        """Initialize a Team instance.

        Args:
            name: Franchise team name.
            owner: Team owner username or entity.
            purse: Remaining salary cap purse.
            max_players: Maximum squad size allowed.
        """
        self.name: str = name
        self.owner: str = owner
        self.purse: int = purse
        self.max_players: int = max_players
        # Aggregation: Team holds references to independent Player objects
        self.players: list[Player] = []

    def add_player(self, player: Player) -> bool:
        """Add a player to the squad if roster limit allows.

        Args:
            player: Player instance to aggregate.

        Returns:
            bool: True if added, False if squad is full.
        """
        if len(self.players) < self.max_players:
            self.players.append(player)
            return True
        return False

    def __str__(self) -> str:
        """Return human-readable team representation."""
        return f"Team(name='{self.name}', owner='{self.owner}', purse={self.purse}, squad={len(self.players)}/{self.max_players})"


class Match:
    """Represents a scheduled fixture between two competing teams."""

    def __init__(self, team1: Union[Team, str], team2: Union[Team, str], date: str) -> None:
        """Initialize a Match fixture.

        Args:
            team1: First participating team or team name.
            team2: Second participating team or team name.
            date: Scheduled match date string.
        """
        self.team1: Union[Team, str] = team1
        self.team2: Union[Team, str] = team2
        self.date: str = date
        self.score1: int = 0
        self.score2: int = 0
        self.played: bool = False

    def record_result(self, score1: int, score2: int) -> None:
        """Record the scores for the match fixture.

        Args:
            score1: Score achieved by team1.
            score2: Score achieved by team2.
        """
        self.score1 = score1
        self.score2 = score2
        self.played = True

    def __str__(self) -> str:
        """Return match fixture details."""
        status = f"{self.score1} - {self.score2}" if self.played else "Upcoming"
        return f"Match({self.team1} vs {self.team2} on {self.date} [{status}])"


class Tournament:
    """Represents an entire tournament edition owning its fixtures.

    Demonstrates COMPOSITION: Tournament owns Match objects.
    If the Tournament is deleted, its matches cease to exist in that context.
    Also demonstrates ASSOCIATION: Auction interacts with Teams without ownership.
    """

    # [Concept: Relationships] Composition — Tournament owns Match (strong ownership)
    def __init__(self, name: str) -> None:
        """Initialize a Tournament instance.

        Args:
            name: Tournament title.
        """
        self.name: str = name
        # Composition: matches are created and lifecycle-managed within the Tournament
        self.matches: list[Match] = []

    def create_fixture(self, team1: Union[Team, str], team2: Union[Team, str], date: str) -> Match:
        """Create and own a new fixture in this tournament.

        Args:
            team1: First team.
            team2: Second team.
            date: Scheduled date.

        Returns:
            Match: Newly composed match instance.
        """
        match = Match(team1, team2, date)
        self.matches.append(match)
        return match

    def __str__(self) -> str:
        """Return tournament string representation."""
        return f"Tournament(name='{self.name}', total_matches={len(self.matches)})"
