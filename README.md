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

Install and run (Windows / PowerShell)
-------------------------------------
Assuming you have cloned the repository and have VS Code installed, follow these steps to set up the project on a new device:

1. Ensure Python 3.8+ is installed. If not, download and install it from https://www.python.org/downloads/.

2. Run the automated setup script to create the virtual environment and install dependencies:

```powershell
.\setup_venv.ps1
```

   This script will:
   - Check for Python installation
   - Create a virtual environment (`.venv`)
   - Activate the virtual environment
   - Install required packages from `requirements.txt`

3. Configure the database. The app uses MySQL by default (`mysql://root@localhost/esports_tournament`). You can either:

   - Install MySQL and create a database named `esports_tournament`, OR
   - For easy local testing, change `app.config['SQLALCHEMY_DATABASE_URI']` in `website/__init__.py` to use SQLite: `sqlite:///esports_dev.db`

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
  - id, name, location, date, max_players

- TournamentRegistration
  - id, tournament_id, team_id, registration_date, status

Notes about migrations and schema
---------------------------------
- This project currently calls `db.create_all()` at app startup in `website/__init__.py`. That will create missing tables for the current models but is not a substitute for proper migrations.
- For production or evolving schema, use Alembic (Flask-Migrate) to track migrations. If you'd like, I can add a `Flask-Migrate` setup and initial migration files.


