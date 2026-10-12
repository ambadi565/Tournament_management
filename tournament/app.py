"""Flask web application providing routes, session authentication, and templates."""

import os
import sys

# Ensure local tournament directory is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# [Concept: Modules] flask module for web framework
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
)
import db
import auth
import players
import teams
import auction
import matches
import standings
import reports
from decorators import web_login_required, web_admin_only

app = Flask(__name__)
# [Concept: Basic I/O, variables, constants, scope] Secret key configuration
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")


@app.route("/")
def index():
    """Root route redirecting based on session authentication status."""
    if session.get("username"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login for web interface."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user_info = auth.check_login(username, password)
        if user_info is not None:
            session["username"] = user_info["username"]
            session["role"] = user_info["role"]
            flash(f"Welcome back, {user_info['username']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration for web interface."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "owner").strip().lower()
        if auth.create_user(username, password, role):
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        flash("Registration failed. Username may already exist or input was invalid.", "danger")
    return render_template("register.html")


@app.route("/logout")
def logout():
    """Clear session data and log out the user."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@web_login_required
def dashboard():
    """Display dashboard with key tournament metrics."""
    stats = standings.get_stats()
    return render_template("dashboard.html", stats=stats)


@app.route("/players")
@web_login_required
def player_list():
    """Display all registered players."""
    player_data = players.list_players()
    return render_template("players.html", players=player_data)


@app.route("/players/add", methods=["POST"])
@web_login_required
@web_admin_only
def player_add():
    """Register a new player via administrator web action."""
    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()
    base_price = request.form.get("base_price", "0").strip()
    try:
        price_val = int(base_price)
    except ValueError:
        price_val = 0

    if players.add_player_web(name, role, price_val):
        flash(f"Player '{name}' added successfully.", "success")
    else:
        flash("Failed to add player. Please verify inputs.", "danger")
    return redirect(url_for("player_list"))


@app.route("/teams")
@web_login_required
def team_list():
    """Display all franchise teams."""
    team_data = teams.list_teams()
    return render_template("teams.html", teams=team_data)


@app.route("/teams/add", methods=["POST"])
@web_login_required
@web_admin_only
def team_add():
    """Create a new team via administrator web action."""
    name = request.form.get("name", "").strip()
    owner = request.form.get("owner", "").strip()
    purse = request.form.get("purse", "0").strip()
    max_players = request.form.get("max_players", "11").strip()
    try:
        purse_val = int(purse)
        max_val = int(max_players) if max_players else 11
    except ValueError:
        purse_val, max_val = 0, 11

    if teams.create_team_web(name, owner, purse_val, max_val):
        flash(f"Team '{name}' created successfully.", "success")
    else:
        flash("Failed to create team. Name must be unique and purse positive.", "danger")
    return redirect(url_for("team_list"))


@app.route("/auction")
@web_login_required
def auction_view():
    """Display live auction room with current player and recent bids."""
    current_player = auction.next_unsold()
    recent = auction.recent_bids(10)
    team_data = teams.list_teams()
    return render_template("auction.html", player=current_player, recent_bids=recent, teams=team_data)


@app.route("/auction/bid", methods=["POST"])
@web_login_required
def auction_bid():
    """Submit a bid for the currently auctioned player."""
    player_id = request.form.get("player_id", "")
    team_id = request.form.get("team_id", "")
    amount = request.form.get("amount", "")
    try:
        success, message = auction.place_bid(int(player_id), int(team_id), int(amount))
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
    except (ValueError, TypeError):
        flash("Invalid bid parameters provided.", "danger")
    return redirect(url_for("auction_view"))


@app.route("/matches")
@web_login_required
def match_list():
    """Display all tournament match fixtures."""
    fixtures = matches.list_matches()
    return render_template("matches.html", matches=fixtures)


@app.route("/matches/generate", methods=["POST"])
@web_login_required
@web_admin_only
def match_generate():
    """Generate round-robin fixtures for all teams."""
    matches.generate_matches()
    flash("Round-robin fixtures generated successfully.", "success")
    return redirect(url_for("match_list"))


@app.route("/matches/<int:match_id>/result", methods=["POST"])
@web_login_required
def match_result(match_id: int):
    """Record scores for a played match fixture."""
    s1 = request.form.get("score1", "0")
    s2 = request.form.get("score2", "0")
    try:
        matches.enter_result_web(match_id, int(s1), int(s2))
        flash(f"Recorded result for Match {match_id}: {s1} - {s2}", "success")
    except (ValueError, TypeError):
        flash("Invalid scores provided.", "danger")
    return redirect(url_for("match_list"))


@app.route("/standings")
@web_login_required
def standings_view():
    """Display points table and tournament standings."""
    table = standings.show_points_table()
    return render_template("standings.html", table=table)


@app.route("/reports")
@web_login_required
def reports_view():
    """Display export reports options."""
    return render_template("reports.html")


@app.route("/reports/export", methods=["POST"])
@web_login_required
def reports_export():
    """Trigger generation of JSON and CSV report files."""
    reports.export_json()
    reports.export_csv()
    flash("Reports exported successfully to report.json and points.csv.", "success")
    return redirect(url_for("reports_view"))


@app.route("/reports/download/<kind>")
@web_login_required
def reports_download(kind: str):
    """Download exported tournament reports."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Check both current directory and tournament directory
    if kind == "json":
        candidates = [
            os.path.join(base_dir, "report.json"),
            os.path.join(os.getcwd(), "report.json"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return send_file(path, as_attachment=True, download_name="report.json", mimetype="application/json")
        reports.export_json()
        target = os.path.join(base_dir, "report.json")
        return send_file(target, as_attachment=True, download_name="report.json", mimetype="application/json")
    elif kind == "csv":
        candidates = [
            os.path.join(base_dir, "points.csv"),
            os.path.join(os.getcwd(), "points.csv"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return send_file(path, as_attachment=True, download_name="points.csv", mimetype="text/csv")
        reports.export_csv()
        target = os.path.join(base_dir, "points.csv")
        return send_file(target, as_attachment=True, download_name="points.csv", mimetype="text/csv")
    flash("Unknown report download format.", "danger")
    return redirect(url_for("reports_view"))


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
