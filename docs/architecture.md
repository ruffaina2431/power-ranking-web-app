# E-Sports Tournament Hub - Architecture Documentation

## Application Overview
The E-Sports Tournament Hub is a Flask-based web application that manages e-sports tournaments, team registrations, and player rankings. It provides functionality for user authentication, team management, tournament organization, and power rankings.

## Project Structure
```
py web app/
├── main.py                 # Application entry point
├── website/                # Main application package
│   ├── __init__.py        # App initialization and configuration
│   ├── auth.py            # Authentication routes and logic
│   ├── models.py          # Database models
│   ├── views.py           # Main application routes
│   ├── static/            # Static files (CSS, JS, images)
│   └── templates/         # Jinja2 HTML templates
```

## Key Components

### 1. Authentication System (auth.py)
- User registration and login
- Password hashing and verification
- Session management
- Access control for protected routes

### 2. Database Models (models.py)
- User: Stores user account information
- Team: Manages team data and rankings
- Player: Handles individual player information
- Tournament: Stores tournament details
- TournamentRegistration: Links teams to tournaments

### 3. Views (views.py)
- Home page with rankings and tournament listings
- Team management (creation, updating)
- Tournament management
- Player roster management
- Registration handling

### 4. Templates
- Base template with common layout
- Home page with search and rankings
- Authentication forms
- Team and tournament management forms

## Data Flow

1. User Registration/Login:
   ```
   Browser -> auth.py -> models.py -> Database
   ```

2. Tournament Registration:
   ```
   Browser -> views.py -> models.py -> Database
   ```

3. Team Rankings Display:
   ```
   Database -> models.py -> views.py -> templates -> Browser
   ```

## Key Features

1. Team Management
   - Create/edit teams
   - Manage player rosters
   - Track team statistics

2. Tournament System
   - Create tournaments
   - Register teams
   - Track results
   - Update rankings

3. Power Rankings
   - Calculate team points
   - Update rankings
   - Display leaderboards

4. Search System
   - Game category search
   - Case-insensitive matching
   - Real-time feedback

## Database Schema

```
User
├── id (Primary Key)
├── email (Unique)
├── password (Hashed)
└── first_name

Team
├── id (Primary Key)
├── name
├── captain_id (Foreign Key -> User)
├── game_name
├── points
├── wins
└── rank

Player
├── id (Primary Key)
├── name
└── team_id (Foreign Key -> Team)

Tournament
├── id (Primary Key)
├── name
├── location
├── date
└── max_teams

TournamentRegistration
├── id (Primary Key)
├── tournament_id (Foreign Key -> Tournament)
├── team_id (Foreign Key -> Team)
└── status
```