"""
Database Models - E-Sports Tournament Hub

This module defines the database structure using SQLAlchemy ORM.
Each class represents a table in the database with defined relationships
and constraints.

Model Relationships:
┌─────────┐     ┌──────┐      ┌─────────
│  User   │──┐  │ Team │────▶[] Player │
└─────────┘  │  └──────┘      └─────────┘
             │      │
             │      │     ┌────────────┐
             └──────┴───▶[]Tournament [] 
                          └────────────┘

Key Relationships:
- User (1) -> (M) Team (Captain relationship)
- Team (1) -> (M) Player
- Team (M) <-> (M) Tournament (through TournamentRegistration)

Data Flow:
1. User creates account -> User model
2. User creates team -> Team model
3. Team adds players -> Player model
4. Team registers for tournament -> TournamentRegistration model

Security Notes:
- Passwords are hashed before storage
- Email addresses must be unique
- Team names must be unique
"""

from flask_login import UserMixin
from sqlalchemy.sql import func
from typing import Optional

from . import db

class User(db.Model, UserMixin):
    """User model representing registered users."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    teams = db.relationship('Team', backref='captain', lazy=True)

class Team(db.Model):
    """Team model representing e-sports teams."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    captain_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    captain_phone = db.Column(db.String(20))
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)
    game_name = db.Column(db.String(150))
    image = db.Column(db.String(255))  # Path to team image
    # pylint: disable=E1102
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    players = db.relationship('Player', backref='team', lazy=True, cascade="all, delete-orphan")
    tournament_registrations = db.relationship('TournamentRegistration', backref='team', lazy=True, cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint('name', name='unique_team_name'),)

    @property
    def has_registrations(self):
        """Check if the team has any tournament registrations."""
        return TournamentRegistration.query.filter_by(team_id=self.id).count() > 0

    def __init__(
        self,
        name: Optional[str] = None,
        captain_id: Optional[int] = None,
        captain_phone: Optional[str] = None,
        points: int = 0,
        wins: int = 0,
        rank: Optional[int] = None,
        game_name: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Typed initializer to help static type-checkers (keeps runtime behavior)."""
        # Call super to preserve SQLAlchemy internals, then set attributes explicitly.
        super().__init__(**kwargs)
        if name is not None:
            self.name = name
        if captain_id is not None:
            self.captain_id = captain_id
        if captain_phone is not None:
            self.captain_phone = captain_phone
        self.points = points
        self.wins = wins
        if rank is not None:
            self.rank = rank
        if game_name is not None:
            self.game_name = game_name

class Player(db.Model):
    """Player model representing team members."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    image = db.Column(db.String(255))  # Path to player image
    # pylint: disable=E1102
    join_date = db.Column(db.DateTime(timezone=True), default=func.now())

    def __init__(self, name: Optional[str] = None, team_id: Optional[int] = None, **kwargs) -> None:
        """Typed initializer for Player."""
        super().__init__(**kwargs)
        if name is not None:
            self.name = name
        if team_id is not None:
            self.team_id = team_id

class Tournament(db.Model):
    """Tournament model representing e-sports tournaments."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))  # Tournament name
    game_name = db.Column(db.String(150))  # Game name for the tournament
    location = db.Column(db.String(50))  # example 'point-a' or 'point-b'
    date = db.Column(db.DateTime(timezone=True))
    max_players = db.Column(db.Integer)
    archived = db.Column(db.Boolean, default=False)
    registrations = db.relationship('TournamentRegistration', backref='tournament', lazy=True)

    def __init__(
        self,
        name: Optional[str] = None,
        game_name: Optional[str] = None,
        location: Optional[str] = None,
        date: Optional[object] = None,
        max_players: Optional[int] = None,
        **kwargs,
    ) -> None:
        """Typed initializer for Tournament."""
        super().__init__(**kwargs)
        if name is not None:
            self.name = name
        if game_name is not None:
            self.game_name = game_name
        if location is not None:
            self.location = location
        if date is not None:
            self.date = date
        if max_players is not None:
            self.max_players = max_players

class TournamentRegistration(db.Model):
    """TournamentRegistration model linking teams to tournaments."""
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    # pylint: disable=E1102
    registration_date = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected

    def __init__(self, tournament_id: Optional[int] = None, team_id: Optional[int] = None, status: Optional[str] = None, **kwargs) -> None:
        """Typed initializer for TournamentRegistration."""
        super().__init__(**kwargs)
        if tournament_id is not None:
            self.tournament_id = tournament_id
        if team_id is not None:
            self.team_id = team_id
        if status is not None:
            self.status = status
