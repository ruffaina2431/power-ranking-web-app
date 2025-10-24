E-Sports Tournament Hub
=======================

Quick start and developer notes

Overview
--------
This is a Flask web application to manage e-sports tournaments, teams, and players. It uses SQLAlchemy for ORM and Flask-Login for authentication. The app was developed to run locally during development and uses a MySQL database by default (see configuration below).

Prerequisites
-------------
- Python 3.10+ (or 3.8+ recommended)
- Git (optional)
- A MySQL server if you want to use the default DB configuration, otherwise you can switch to SQLite (see below)

Recommended VS Code extensions
-----------------------------
- ms-python.python
- ms-python.vscode-pylance
- eamodio.gitlens
- blackboxapp.blackbox (already recommended in .vscode/extensions.json)

Install and run (Windows / PowerShell)
-------------------------------------
1. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Provide DB connection info. The app uses the connection string set in `website/__init__.py` by default (`mysql://root@localhost/esports_tournament`). You can either:

- Create a MySQL database named `esports_tournament` and make sure a root user can connect (for local dev), OR
- Change `app.config['SQLALCHEMY_DATABASE_URI']` in `website/__init__.py` to use SQLite for easy local testing, e.g. `sqlite:///esports_dev.db`.

4. (Optional) Create a `.env` file or set environment variables (see `.env.example`).

5. Run the app:

```powershell
python main.py
```

6. Open http://127.0.0.1:5000 in your browser.

Database schema and where it's defined
-------------------------------------
The database tables are defined in `website/models.py` (SQLAlchemy models). Key models and fields:

- User
  - id, email (unique), password (hashed), first_name

- Team
  - id, name (unique), captain_id, captain_phone, points, wins, rank, game_name, created_date

- Player
  - id, name, team_id, join_date

- Tournament
  - id, name, location, date, max_teams

- TournamentRegistration
  - id, tournament_id, team_id, registration_date, status

Notes about migrations and schema
---------------------------------
- This project currently calls `db.create_all()` at app startup in `website/__init__.py`. That will create missing tables for the current models but is not a substitute for proper migrations.
- For production or evolving schema, use Alembic (Flask-Migrate) to track migrations. If you'd like, I can add a `Flask-Migrate` setup and initial migration files.


