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

from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    teams = db.relationship('Team', backref='captain', lazy=True)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    captain_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    captain_phone = db.Column(db.String(20))
    points = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer)
    game_name = db.Column(db.String(150))
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    players = db.relationship('Player', backref='team', lazy=True)
    tournament_registrations = db.relationship('TournamentRegistration', backref='team', lazy=True)

    __table_args__ = (db.UniqueConstraint('name', name='unique_team_name'),)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    join_date = db.Column(db.DateTime(timezone=True), default=func.now())

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))  # Tournament name
    location = db.Column(db.String(50))  # example 'point-a' or 'point-b'
    date = db.Column(db.DateTime(timezone=True))
    max_teams = db.Column(db.Integer)
    registrations = db.relationship('TournamentRegistration', backref='tournament', lazy=True)

class TournamentRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    registration_date = db.Column(db.DateTime(timezone=True), default=func.now())
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
