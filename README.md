E-Sports Tournament Hub
=======================

Quick start and developer notes

Overview
--------
This is a Flask web application to manage e-sports tournaments, teams, and players. It uses SQLAlchemy for ORM and Flask-Login for authentication. The app was developed to run locally during development and uses a MySQL database by default (see configuration below).

Goals
-----
The primary goals of this project are:
- Provide a centralized platform for managing e-sports tournaments, teams, and players.
- Enable user authentication and role-based access (e.g., admin controls).
- Facilitate team creation, player management, and tournament registrations.
- Maintain dynamic power rankings based on tournament performance.
- Support filtering and sorting of teams by game/category and various metrics.

Constraints
----------
The application operates under the following constraints:
- Built using Flask web framework for simplicity and rapid development.
- Relies on SQLAlchemy ORM for database interactions, with MySQL as default (SQLite as fallback for local testing).
- Designed primarily for local development; production deployment requires additional configuration (e.g., WSGI server).
- Certain features (e.g., tournament creation, ranking management) are restricted to admin users.
- Assumes data integrity through user inputs and does not include advanced validation or error recovery mechanisms.
- Limited to basic API endpoints; not designed for high-traffic or real-time applications.

Features
--------
- **User Authentication**: Sign up, login, and session management with Flask-Login.
- **Team Management**: Create, edit, and delete teams; manage player rosters.
- **Tournament Management**: Create and manage tournaments (admin only); view upcoming tournaments.
- **Tournament Registration**: Register teams for tournaments; approve/reject registrations (admin only).
- **Dynamic Rankings**: View and manage team rankings based on points and wins.
- **Filtering and Sorting**: Filter teams by game/category and sort by rank, name, points, or wins.
- **Admin Controls**: Manage tournaments, rankings, and registrations.
- **API Endpoints**: Basic API for tournament details.

Project Structure
-----------------
```
power-ranking-web-app/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup_venv.ps1          # PowerShell script for virtual environment setup
├── README.md               # This file
├── docs/                   # Documentation
│   ├── architecture.md    # System architecture
│   ├── templates.md       # Template documentation
│   └── user_flows.md      # User flow diagrams
├── website/                # Main application package
│   ├── __init__.py         # Flask app factory
│   ├── auth.py             # Authentication routes
│   ├── models.py           # Database models
│   ├── views.py            # Main application routes
│   └── templates/          # Jinja2 templates
│       ├── base.html       # Base template
│       ├── home.html       # Home page
│       ├── login.html      # Login page
│       ├── sign_up.html    # Sign up page
│       ├── team_form.html  # Team creation/editing
│       ├── team_list.html  # Team list
│       ├── team_detail.html# Team details
│       ├── player_form.html# Player editing
│       ├── tournament_form.html  # Tournament creation/editing
│       ├── tournament_list.html  # Tournament list
│       ├── tournament_join.html  # Join tournament
│       ├── tournament_registrations.html  # View registrations
│       ├── manage_rankings.html  # Admin ranking management
│       └── edit_ranking.html     # Edit team ranking
└── .gitignore              # Git ignore rules
```

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

Usage
-----
- **Home Page**: View team rankings, upcoming tournaments, and filter by game/category.
- **Authentication**: Sign up or log in to access team and tournament features.
- **Team Management**: Create and manage your teams and players.
- **Tournaments**: Admins can create tournaments; users can register teams.
- **Admin Panel**: Manage rankings and approve registrations.
- For detailed user flows, see `docs/user_flows.md`.

API Endpoints
-------------
- `GET /api/tournament/<location>`: Get tournament details by location (JSON response with game_name and name).

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
  - id, name, location, date, max_players, game_name, archived

- TournamentRegistration
  - id, tournament_id, team_id, registration_date, status

Troubleshooting
---------------
- **ModuleNotFoundError (e.g., 'No module named 'flask_apscheduler'')**: This indicates a missing dependency. Ensure you have activated the virtual environment (`.venv\Scripts\activate` on Windows) and run `pip install -r requirements.txt` to install all required packages. If using the setup script, verify it completed successfully without errors.
- **Database connection errors**: If using MySQL, ensure the server is running and the database exists. For SQLite, no additional setup is needed.
- **Port already in use**: If port 5000 is occupied, stop other processes or modify the port in `main.py`.
- **Permission errors**: Run commands as administrator if necessary, especially for virtual environment creation.



