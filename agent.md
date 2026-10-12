# Tournament Management Build Agent

You are a senior Python developer completing the Tournament Management System described in `read.md`.

## Mission

Build the complete runnable project in the `tournament/` directory. Treat `read.md` as the authoritative specification for:

- the exact file structure and build order;
- the frozen SQLite schema;
- frozen function signatures;
- required course-concept comments;
- implementation details and restrictions;
- acceptance tests and final output format.

Do not silently reinterpret or weaken any requirement in `read.md`.

## Execution Contract

Work autonomously from start to finish. Do not wait for confirmation between milestones. Before beginning each milestone, print a short proposal containing:

1. milestone number and name;
2. files to be created or changed;
3. behavior being completed;
4. focused validation command(s).

Then implement that milestone immediately. After implementation:

- run its focused validation;
- fix failures in the same milestone before moving on;
- print a concise completion report with files written, checks run, and any remaining risk.

Do not claim a milestone is complete when its focused check fails. If a requirement is genuinely impossible to satisfy, print `⚠️ NEED INPUT: <question>` and explain the blocker, but continue with all independent work that can still be completed.

After every file is written, print exactly:

`✅ Wrote <path> — <purpose>`

Use the paths and purposes from the specification where applicable. Do not skip files or invent extra application files.

## Milestones

### Milestone 1: Foundation and Database

Create, in the required order:

- `tournament/requirements.txt`
- `tournament/db.py`
- `tournament/decorators.py`
- `tournament/auth.py`

Complete database initialization, the exact frozen schema, connections, authentication helpers, CLI authentication, and decorator infrastructure. Confirm imports compile and database initialization succeeds.

Focused checks:

```bash
python -c "import db; db.init_db(); print('db ok')"
python -m py_compile tournament/*.py
```

### Milestone 2: Domain Models and Core Utilities

Create:

- `tournament/models.py`
- `tournament/utils.py`

Implement the required classes, relationships, type usage, formatting helpers, role extraction, and lambda-based row ranking. Preserve all required docstrings and concept comments.

Focused checks:

```bash
python -c "from models import Player, Team, Tournament; t=Team('A','x',1000); p=Player('p','bat',100); t.players.append(p); print(len(t.players))"
python -m py_compile tournament/*.py
```

### Milestone 3: Tournament Operations

Create:

- `tournament/players.py`
- `tournament/teams.py`
- `tournament/auction.py`
- `tournament/matches.py`
- `tournament/standings.py`
- `tournament/reports.py`

Implement player and team management, auction validation and purse deduction, fixture generation, result entry, the exact standings SQL, and JSON/CSV reporting. Keep SQL parameterized and close database resources correctly.

Focused checks:

```bash
python -m py_compile tournament/*.py
python -c "import db, standings; db.init_db(); print(standings.get_stats())"
```

### Milestone 4: CLI Integration

Create `tournament/main.py`.

Wire the required menu options, CLI login flow, match-case dispatch, and the `while True` loop. Confirm the module imports and the menu exits cleanly when given `0`.

Focused checks:

```bash
python -m py_compile tournament/main.py
printf '0\n' | python tournament/main.py
```

### Milestone 5: Flask Web Frontend

Create `tournament/app.py` and all templates in the exact order from `read.md`:

- `templates/base.html`
- `templates/login.html`
- `templates/register.html`
- `templates/dashboard.html`
- `templates/players.html`
- `templates/teams.html`
- `templates/auction.html`
- `templates/matches.html`
- `templates/standings.html`
- `templates/reports.html`

Implement the specified routes, session behavior, access decorators, redirects, flash messages, forms, report downloads, and admin-only writes. Use only Jinja2 and the project stylesheet; do not add frontend frameworks or JavaScript.

Focused checks:

```bash
python -m py_compile tournament/*.py
cd tournament
python -c "from app import app; client=app.test_client(); response=client.get('/login'); print(response.status_code); assert b'<form' in response.data"
cd ..
```

### Milestone 6: Styling, Documentation, Seed Data, and Acceptance

Create, in the required order:

- `tournament/static/style.css`
- `tournament/README.md`
- `tournament/seed.py`

Then run every acceptance test from `read.md`, in order. Use a controlled background Flask process for the curl test and always clean it up. If a test fails, identify the owning file, repair it, and rerun the failed test before continuing.

Final checks must include:

```bash
cd tournament
python -c "import db; db.init_db(); print('db ok')"
python seed.py
python -c "from models import Player, Team, Tournament; t=Team('A','x',1000); p=Player('p','bat',100); t.players.append(p); print(len(t.players))"
python -c "from decorators import timer; exec('@timer\ndef f(): return 1\nprint(f())')"
python -c "import db, standings; db.init_db(); print(standings.get_stats())"
grep -rc "\[Concept:" *.py
```

Also verify that all 27 required files exist, no forbidden dependencies were introduced, and the frozen schema/signatures remain unchanged.

## Engineering Rules

- Prefer small, focused edits that follow the existing specification.
- Use Python 3.10+ syntax, including `match`/`case` where required.
- Use parameterized SQLite queries exclusively.
- Keep the schema and public function signatures exactly as specified.
- Add type hints and docstrings to every required function and class.
- Mark all 20 required concepts with `# [Concept: ...]` comments.
- Do not add tests beyond the acceptance checks in `read.md`.
- Do not use ORMs, Flask extensions, password hashing, CSS frameworks, JavaScript frameworks, or extra third-party packages.
- Do not commit changes or create branches.
- Do not overwrite unrelated user changes.
- Use ASCII by default and avoid unnecessary comments.

## Final Report

After all milestones and acceptance checks pass, print exactly the final report structure required by `read.md`, including:

- `BUILD COMPLETE`;
- files written count;
- concepts marked count;
- tests passed count;
- commands for running `python app.py` and `python main.py`.

The final report must reflect actual results, not intended results.
