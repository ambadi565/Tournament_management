"""Decorators module for access control, performance timing, and audit logging."""

# [Concept: Modules] functools, time, datetime, os
import functools
import time
import os
from datetime import datetime
from typing import Any, Callable
from flask import session, redirect, url_for, flash


def get_current_user_info() -> tuple[str, str]:
    """Retrieve current CLI user information.

    Returns:
        tuple[str, str]: (username, role)
    """
    try:
        from auth import current_user
        username = current_user.get("name") or "anonymous"
        role = current_user.get("role") or "none"
        return str(username), str(role)
    except (ImportError, AttributeError):
        return "anonymous", "none"


# [Concept: Decorators] Access control decorator for CLI authentication
def login_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Ensure the user is logged in before executing a CLI action.

    Args:
        func: The function to decorate.

    Returns:
        Wrapped function checking current_user status.
    """
    # [Concept: *args and **kwargs] Arbitrary arguments forwarding
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from auth import current_user
        if not current_user.get("name"):
            print("Access denied: You must be logged in to perform this action.")
            return None
        return func(*args, **kwargs)

    return wrapper


# [Concept: Decorators] Role-based authorization decorator for CLI
def admin_only(func: Callable[..., Any]) -> Callable[..., Any]:
    """Ensure the user has an admin role before executing a CLI action.

    Args:
        func: The function to decorate.

    Returns:
        Wrapped function checking admin role.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        from auth import current_user
        if current_user.get("role") != "admin":
            print("Access denied: Admin privileges required.")
            return None
        return func(*args, **kwargs)

    return wrapper


# [Concept: Decorators] Action logger decorator recording execution to actions.log
def log_action(func: Callable[..., Any]) -> Callable[..., Any]:
    """Log function execution to actions.log with timestamp, user, and function name.

    Args:
        func: The function to decorate.

    Returns:
        Wrapped function that records audit trail.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        username, _ = get_current_user_info()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{now_str} | {username} | {func.__name__}\n"
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "actions.log")
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except OSError as e:
            print(f"Failed to write to actions.log: {e}")
        return func(*args, **kwargs)

    return wrapper


# [Concept: Decorators] Performance timing decorator
def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """Measure and print the execution time of a function to standard output.

    Args:
        func: The function to decorate.

    Returns:
        Wrapped function printing elapsed time.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"[{func.__name__}] executed in {elapsed:.4f}s")
        return result

    return wrapper


# [Concept: Decorators] Web session login verification decorator
def web_login_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Ensure the web request has an active user session.

    Args:
        func: The view function to decorate.

    Returns:
        Wrapped view function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not session.get("username"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


# [Concept: Decorators] Web session admin role authorization decorator
def web_admin_only(func: Callable[..., Any]) -> Callable[..., Any]:
    """Ensure the web request has admin privileges in session.

    Args:
        func: The view function to decorate.

    Returns:
        Wrapped view function.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if session.get("role") != "admin":
            flash("Admin access required for this action.", "danger")
            return redirect(url_for("dashboard"))
        return func(*args, **kwargs)

    return wrapper
