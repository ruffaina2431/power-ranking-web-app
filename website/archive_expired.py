"""
Background task for archiving expired tournaments.

This module contains the function that is scheduled to run periodically
to automatically archive tournaments that have expired.
"""

from .models import Tournament, TournamentRegistration, AuditLog, db
from sqlalchemy.sql import func
import json

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
                print(f"Auto-archiving expired tournament: {tournament.name} (ID: {tournament.id})")
                tournament.archived = True
                tournament.hide = True  # Hide expired tournaments

                # Set all approved registrations for this tournament to 'archived'
                approved_regs = TournamentRegistration.query.filter_by(tournament_id=tournament.id, status='approved').all()
                for reg in approved_regs:
                    reg.status = 'archived'

                # Log the automatic archiving
                audit_log = AuditLog(
                    user_id=None,  # Automatic action
                    action='auto_archive_tournament',
                    target_type='tournament',
                    target_id=tournament.id,
                    details=json.dumps({
                        'tournament_name': tournament.name,
                        'location': tournament.location,
                        'date': tournament.date.isoformat()
                    })
                )
                db.session.add(audit_log)

            db.session.commit()
            print(f"Successfully auto-archived {len(expired_tournaments)} expired tournaments.")
        else:
            print("No expired tournaments found to archive.")

    except Exception as e:
        print(f"Error archiving expired tournaments: {e}")
        db.session.rollback()
