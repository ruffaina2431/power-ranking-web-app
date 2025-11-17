"""
Background task for archiving expired tournaments.

This module contains the function that is scheduled to run periodically
to automatically archive tournaments that have expired.
"""

from .models import Tournament, db
from sqlalchemy.sql import func

def archive_expired_tournaments():
    """
    Archive tournaments that have expired.

    This function is called by the APScheduler to automatically archive
    tournaments whose date has passed and are not already archived.
    """
    try:
        # Find tournaments where date < now and not already archived
        expired_tournaments = Tournament.query.filter(
            Tournament.date < func.now(),
            Tournament.archived == False
        ).all()

        if expired_tournaments:
            for tournament in expired_tournaments:
                tournament.archived = True
                tournament.hide = True  # Hide expired tournaments
                print(f"Auto-archived expired tournament: {tournament.name} (ID: {tournament.id})")

            db.session.commit()
            print(f"Successfully auto-archived {len(expired_tournaments)} expired tournaments.")
        else:
            print("No expired tournaments found to archive.")

    except Exception as e:
        print(f"Error archiving expired tournaments: {e}")
        db.session.rollback()
