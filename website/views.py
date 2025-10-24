"""
Views Blueprint for E-Sports Tournament Hub.

This module defines all the main application routes including home page,
team management, player management, tournament operations, and CRUD functionality.
Handles user interactions for managing teams, players, and tournament registrations.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import Team, Player, Tournament, TournamentRegistration
from . import db
from sqlalchemy.sql import func

views = Blueprint('views', __name__)

@views.route('/')
def home():
    """
    Home page route displaying tournament information and team rankings.
    """
    # Get filter parameters
    category = request.args.get('category', 'VALORANT')
    sort_by = request.args.get('sort', 'rank')
    order = request.args.get('order', 'asc')

    # Filter teams based on search category
    if category != 'VALORANT':
        # First try to match game_name
        teams_query = Team.query.filter(Team.game_name.ilike(f'%{category}%'))
        
        # If no teams found by game_name, then try tournament names as fallback
        if teams_query.first() is None:
            teams_query = Team.query.join(TournamentRegistration).join(Tournament).filter(
                Tournament.name.ilike(f'%{category}%')
            ).distinct()
    else:
        # Default: show VALORANT teams
        teams_query = Team.query.filter(Team.game_name.ilike('VALORANT'))

    # Apply sorting
    if sort_by == 'rank':
        if order == 'desc':
            teams_query = teams_query.order_by(func.isnull(Team.rank), Team.rank.desc())
        else:
            teams_query = teams_query.order_by(func.isnull(Team.rank), Team.rank.asc())
    elif sort_by == 'name':
        if order == 'desc':
            teams_query = teams_query.order_by(Team.name.desc())
        else:
            teams_query = teams_query.order_by(Team.name.asc())
    elif sort_by == 'points':
        if order == 'desc':
            teams_query = teams_query.order_by(Team.points.desc())
        else:
            teams_query = teams_query.order_by(Team.points.asc())
    elif sort_by == 'wins':
        if order == 'desc':
            teams_query = teams_query.order_by(Team.wins.desc())
        else:
            teams_query = teams_query.order_by(Team.wins.asc())

    teams = teams_query.limit(20).all()

    # Update rankings for the current filtered set
    if category != 'VALORANT':
        # Rank within the filtered teams
        ranked_teams = Team.query.join(TournamentRegistration).join(Tournament).filter(
            Tournament.name.ilike(f'%{category}%')
        ).distinct().order_by(Team.points.desc(), Team.wins.desc()).all()
    else:
        # Global rankings
        ranked_teams = Team.query.order_by(Team.points.desc(), Team.wins.desc()).all()

    for i, team in enumerate(ranked_teams, 1):
        team.rank = i
    db.session.commit()

    # Get all upcoming tournaments (not filtered by category)
    upcoming_tournaments = Tournament.query.filter(
        Tournament.date >= func.now()
    ).order_by(Tournament.date.asc()).all()

    # Get available categories from tournament names
    categories = db.session.query(Tournament.name).distinct().all()
    categories = [cat[0] for cat in categories]

    return render_template("home.html", teams=teams, tournaments=upcoming_tournaments,
                         current_category=category, categories=categories, sort_by=sort_by, order=order)

@views.route('/register/point-a')
@login_required
def register_point_a():
    """Route for Point A tournament registration."""
    return redirect(url_for('views.home', location='point-a'))

@views.route('/register/point-b')
@login_required
def register_point_b():
    """Route for Point B tournament registration."""
    return redirect(url_for('views.home', location='point-b'))

@views.route('/register-team', methods=['POST'])
@login_required
def register_team():
    """Handle team registration form submission."""
    if request.method == 'POST':
        team_name = request.form.get('teamName')
        captain_phone = request.form.get('captainPhone')
        tournament_location = request.form.get('tournamentLocation')

        # Check if team name already exists
        if Team.query.filter_by(name=team_name).first():
            flash('Team name already exists!', category='error')
            return redirect(url_for('views.home'))

        # Create new team
        new_team = Team(
            name=team_name,
            captain_id=current_user.id,
            captain_phone=captain_phone
        )
        db.session.add(new_team)

        # Add players to team
        for i in range(1, 6):
            player_name = request.form.get(f'player{i}')
            if player_name:
                new_player = Player(name=player_name, team=new_team)
                db.session.add(new_player)

        try:
            db.session.commit()

            # If tournament location is provided, register for the tournament
            if tournament_location:
                tournament = Tournament.query.filter_by(
                    location=tournament_location,
                ).order_by(Tournament.date.desc()).first()

                if tournament:
                    # Check if already registered
                    existing_reg = TournamentRegistration.query.filter_by(
                        tournament_id=tournament.id,
                        team_id=new_team.id
                    ).first()

                    if not existing_reg:
                        registration = TournamentRegistration(
                            tournament_id=tournament.id,
                            team_id=new_team.id
                        )
                        db.session.add(registration)
                        db.session.commit()
                        flash('Team registered and tournament registration successful!', category='success')
                    else:
                        flash('Team registered successfully! (Already registered for tournament)', category='success')
                else:
                    flash('Team registered successfully!', category='success')
            else:
                flash('Team registered successfully!', category='success')

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering the team.', category='error')

        return redirect(url_for('views.home'))

@views.route('/tournament-register/<location>', methods=['POST'])
@login_required
def tournament_register(location):
    """Handle tournament registration."""
    team = Team.query.filter_by(captain_id=current_user.id).first()
    
    if not team:
        flash('You need to register a team first!', category='error')
        return redirect(url_for('views.home'))
    
    tournament = Tournament.query.filter_by(
        location=location,
    ).order_by(Tournament.date.desc()).first()
    
    if not tournament:
        flash('No upcoming tournament found for this location!', category='error')
        return redirect(url_for('views.home'))
    
    # Check if already registered
    existing_reg = TournamentRegistration.query.filter_by(
        tournament_id=tournament.id,
        team_id=team.id
    ).first()
    
    if existing_reg:
        flash('Your team is already registered for this tournament!', category='error')
        return redirect(url_for('views.home'))
    
    # Register for tournament
    registration = TournamentRegistration(
        tournament_id=tournament.id,
        team_id=team.id
    )
    
    db.session.add(registration)
    db.session.commit()
    
    flash('Successfully registered for the tournament!', category='success')
    return redirect(url_for('views.home'))

# CRUD for Teams

@views.route('/teams')
@login_required
def teams():
    """List all teams for the current user."""
    user_teams = Team.query.filter_by(captain_id=current_user.id).all()
    return render_template('team_list.html', teams=user_teams)

@views.route('/team/<int:team_id>')
@login_required
def team_detail(team_id):
    """View details of a specific team."""
    team = Team.query.get_or_404(team_id)
    if team.captain_id != current_user.id:
        abort(403)
    return render_template('team_detail.html', team=team)

@views.route('/team/create', methods=['GET', 'POST'])
@login_required
def team_create():
    """Create a new team."""
    if request.method == 'POST':
        team_name = request.form.get('name')
        captain_phone = request.form.get('captain_phone')

        if Team.query.filter_by(name=team_name).first():
            flash('Team name already exists!', category='error')
            return redirect(url_for('views.team_create'))

        new_team = Team(
            name=team_name,
            captain_id=current_user.id,
            captain_phone=captain_phone
        )
        db.session.add(new_team)
        db.session.commit()
        flash('Team created successfully!', category='success')
        return redirect(url_for('views.teams'))

    return render_template('team_form.html', action='Create')

@views.route('/team/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def team_edit(team_id):
    """Edit an existing team."""
    team = Team.query.get_or_404(team_id)
    if team.captain_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        team.name = request.form.get('name')
        team.captain_phone = request.form.get('captain_phone')
        db.session.commit()
        flash('Team updated successfully!', category='success')
        return redirect(url_for('views.team_detail', team_id=team.id))

    return render_template('team_form.html', team=team, action='Edit')

@views.route('/team/<int:team_id>/delete', methods=['POST'])
@login_required
def team_delete(team_id):
    """Delete a team."""
    team = Team.query.get_or_404(team_id)
    if team.captain_id != current_user.id:
        abort(403)

    db.session.delete(team)
    db.session.commit()
    flash('Team deleted successfully!', category='success')
    return redirect(url_for('views.teams'))

# CRUD for Players

@views.route('/team/<int:team_id>/add-player', methods=['GET', 'POST'])
@login_required
def add_player(team_id):
    """Add a player to a team."""
    team = Team.query.get_or_404(team_id)
    if team.captain_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        player_name = request.form.get('name')
        if player_name:
            new_player = Player(name=player_name, team=team)
            db.session.add(new_player)
            db.session.commit()
            flash('Player added successfully!', category='success')
            return redirect(url_for('views.team_detail', team_id=team.id))

    return render_template('player_form.html', team=team, action='Add')

@views.route('/player/<int:player_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    """Edit a player's name."""
    player = Player.query.get_or_404(player_id)
    if player.team.captain_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        player.name = request.form.get('name')
        db.session.commit()
        flash('Player updated successfully!', category='success')
        return redirect(url_for('views.team_detail', team_id=player.team_id))

    return render_template('player_form.html', player=player, action='Edit')

@views.route('/player/<int:player_id>/delete', methods=['POST'])
@login_required
def delete_player(player_id):
    """Remove a player from a team."""
    player = Player.query.get_or_404(player_id)
    if player.team.captain_id != current_user.id:
        abort(403)

    db.session.delete(player)
    db.session.commit()
    flash('Player removed successfully!', category='success')
    return redirect(url_for('views.team_detail', team_id=player.team_id))

# CRUD for Tournaments (assuming admin access, for simplicity all logged-in users can manage for now)

@views.route('/tournaments')
@login_required
def tournaments():
    """List all tournaments."""
    all_tournaments = Tournament.query.all()
    return render_template('tournament_list.html', tournaments=all_tournaments)

@views.route('/tournament/create', methods=['GET', 'POST'])
@login_required
def tournament_create():
    """Create a new tournament."""
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        date = request.form.get('date')
        max_teams = request.form.get('max_teams')

        new_tournament = Tournament(
            name=name,
            location=location,
            date=date,
            max_teams=int(max_teams)
        )
        db.session.add(new_tournament)
        db.session.commit()
        flash('Tournament created successfully!', category='success')
        return redirect(url_for('views.tournaments'))

    return render_template('tournament_form.html', action='Create')

@views.route('/tournament/<int:tournament_id>/edit', methods=['GET', 'POST'])
@login_required
def tournament_edit(tournament_id):
    """Edit an existing tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)

    if request.method == 'POST':
        tournament.name = request.form.get('name')
        tournament.location = request.form.get('location')
        tournament.date = request.form.get('date')
        tournament.max_teams = int(request.form.get('max_teams'))
        db.session.commit()
        flash('Tournament updated successfully!', category='success')
        return redirect(url_for('views.tournaments'))

    return render_template('tournament_form.html', tournament=tournament, action='Edit')

@views.route('/tournament/<int:tournament_id>/delete', methods=['POST'])
@login_required
def tournament_delete(tournament_id):
    """Delete a tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)

    db.session.delete(tournament)
    db.session.commit()
    flash('Tournament deleted successfully!', category='success')
    return redirect(url_for('views.tournaments'))

@views.route('/tournament/<int:tournament_id>/registrations')
@login_required
def tournament_registrations(tournament_id):
    """View registrations for a tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)
    registrations = TournamentRegistration.query.filter_by(tournament_id=tournament_id).all()
    return render_template('tournament_registrations.html', tournament=tournament, registrations=registrations)
