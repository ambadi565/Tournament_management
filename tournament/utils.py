"""Utility helper functions demonstrating data types, operators, sequences, strings, functions, and lambdas."""

# [Concept: Data types] int, float, str, bool, list, tuple, set, dict
from typing import Any, Optional, Union


# [Concept: Functions] Function Type 1: No arguments, no return value
def print_separator() -> None:
    """Print a visual dividing line for console output."""
    print("=" * 60)


# [Concept: Functions] Function Type 2: Arguments, no return value
def log_metric(metric_name: str, value: float) -> None:
    """Log a named performance metric to console without returning data.

    Args:
        metric_name: Label for the metric.
        value: Numeric value.
    """
    print(f"[METRIC] {metric_name}: {value:.2f}")


# [Concept: Functions] Function Type 3: No arguments, with return value
def get_default_config() -> dict[str, Any]:
    """Retrieve default system configuration settings.

    Returns:
        dict[str, Any]: Default configuration key-value mapping.
    """
    # [Concept: Data types] dict demonstration
    return {"version": "1.0.0", "max_teams": 8, "default_purse": 1000}


# [Concept: Functions] Function Type 4: Arguments, with return value
# [Concept: Strings] strip(), title(), upper(), split(), join(), f-strings, .format()
def format_currency(n: Union[int, float]) -> str:
    """Format a numeric value into a stylized currency string.

    Args:
        n: Numeric amount.

    Returns:
        str: Formatted currency representation.
    """
    # [Concept: Operators] arithmetic and relational operators
    if n is None:  # [Concept: Operators] identity operator (is None)
        return "$0"
    amount: float = float(n)
    if amount < 0:
        return f"-${abs(amount):,.0f}"
    # Demonstration of f-strings and .format()
    formatted = "${:,.0f}".format(amount)
    return f"{formatted}"


def clean_string_data(text: str) -> str:
    """Demonstrate string methods: strip(), title(), upper(), split(), join().

    Args:
        text: Raw input string.

    Returns:
        str: Transformed string.
    """
    # [Concept: Strings] strip(), split(), join(), title()
    cleaned = text.strip()
    words = cleaned.split(" ")
    joined = " ".join(words)
    return joined.title()


# [Concept: Sequences] set (unique roles), list, tuple, dict
def unique_roles(players: list[Any]) -> set[str]:
    """Extract the set of unique roles across a collection of player records.

    Args:
        players: Iterable containing Player objects, dicts, or tuples.

    Returns:
        set[str]: Unique role titles.
    """
    roles: set[str] = set()
    for p in players:
        # [Concept: Operators] membership (in), logical (and/or/not)
        if hasattr(p, "role"):
            role_val = str(p.role)
        elif isinstance(p, dict) and "role" in p:
            role_val = str(p["role"])
        elif isinstance(p, (tuple, list)) and len(p) > 2:
            role_val = str(p[2])
        else:
            role_val = "Unknown"

        if role_val and role_val not in roles:
            roles.add(role_val.title())
    return roles


# [Concept: Lambda] Lambda function used for sorting rows
def rank_rows(rows: list[Any], key_index: int = 1, reverse: bool = True) -> list[Any]:
    """Sort and rank tabular rows using a custom lambda key function.

    Args:
        rows: Sequence of list or tuple records.
        key_index: Column index to sort by.
        reverse: Whether to sort descending.

    Returns:
        list[Any]: Ranked and ordered rows.
    """
    # [Concept: Lambda] sorted(rows, key=lambda ...)
    return sorted(rows, key=lambda r: (r[key_index] if len(r) > key_index else 0), reverse=reverse)


def calculate_split_share(total: int, parts: int) -> int:
    """Demonstrate arithmetic operators: +=, //, %.

    Args:
        total: Total amount.
        parts: Number of divisions.

    Returns:
        int: Share per part.
    """
    # [Concept: Operators] arithmetic (+=, //, %)
    if parts <= 0:
        return 0
    quotient = total // parts
    remainder = total % parts
    quotient += 1 if remainder > 0 else 0
    return quotient
