# Tournament Management System

A Python tournament management system with both a command-line interface and a Flask web interface. It supports user authentication, player registration, team management, player auctions, round-robin fixtures, match results, standings, and JSON/CSV reports.

## Requirements

- Python 3.10+
- Flask 3.0+

## Setup

```bash
cd tournament
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
```

## Run

From the `tournament/` directory:

```bash
# Optional: add demo users, teams, and players
python seed.py

# Start the CLI
python main.py

# Start the web interface
python app.py
```

Open the web interface at <http://127.0.0.1:5000>.

The seed data provides these demo accounts:

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `admin` | Administrator |
| `owner` | `owner` | Team owner |

## Project Structure

```text
Tournament_management/
├── tournament/
│   ├── app.py              # Flask web application
│   ├── main.py             # CLI application
│   ├── db.py               # SQLite schema and connections
│   ├── models.py           # Domain models
│   ├── templates/          # Jinja2 templates
│   └── static/             # Web styles
└── .gitignore              # Local and generated files excluded from Git
```

SQLite creates `tournament/tournament.db` automatically on first run. Reports are exported as `report.json` and `points.csv`; local runtime files, caches, virtual environments, and secrets are excluded by the root `.gitignore`.

## Main Workflows

1. Register or log in to an account.
2. Create teams and register players.
3. Auction players while enforcing purse and squad limits.
4. Generate fixtures and enter match results.
5. Review the SQL-backed points table.
6. Export tournament and standings reports.
