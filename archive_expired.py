#!/usr/bin/env python3
"""
Script to archive expired tournaments.

This script checks for tournaments whose date has passed and automatically
archives them by setting the 'archived' flag to True.
"""

from website import create_app, db
from website.models import Tournament
from sqlalchemy.sql import func

def archive_expired_tournaments():
    """Archive tournaments that have expired."""
    app = create_app()
    with app.app_context():
        # Find tournaments where date < now and not already archived
        expired_tournaments = Tournament.query.filter(
            Tournament.date < func.now(),
            Tournament.archived == False
        ).all()

        print(f"Found {len(expired_tournaments)} expired tournaments to archive.")

        for tournament in expired_tournaments:
            print(f"Archiving tournament: {tournament.name} (ID: {tournament.id})")
            tournament.archived = True

        if expired_tournaments:
            db.session.commit()
            print(f"Successfully archived {len(expired_tournaments)} tournaments.")
        else:
            print("No expired tournaments found.")

if __name__ == "__main__":
    archive_expired_tournaments()
