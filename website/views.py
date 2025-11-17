"""
Views Blueprint for E-Sports Tournament Hub.

This module defines all the main application routes including home page,
team management, player management, tournament operations, and CRUD functionality.
Handles user interactions for managing teams, players, and tournament registrations.

Route Structure:
- / (home): Displays tournament info and team rankings
- /teams: Team management for authenticated users
- /tournaments: Tournament management for admins
- /manage-rankings: Ranking management for admins

Key Features:
- Team creation and management
- Player roster management
- Tournament registration
- Dynamic team rankings
- Tournament scheduling
- Admin controls for tournament and ranking management

Dependencies:
- Flask for routing and templating
- SQLAlchemy for database operations
- Flask-Login for user session management
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, make_response
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from functools import wraps
from datetime import datetime
import os
import json
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

from .models import Team, Player, Tournament, TournamentRegistration, AuditLog
from . import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

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

    # Filter teams based on search category, only include teams with approved registrations
    if category != 'VALORANT':
        # First try to match game_name
        teams_query = Team.query.join(TournamentRegistration).filter(
            TournamentRegistration.status == 'approved',
            Team.game_name.ilike(f'%{category}%')
        )

        # If no teams found by game_name, then try tournament names as fallback
        if teams_query.first() is None:
            teams_query = Team.query.join(TournamentRegistration).join(Tournament).filter(
                TournamentRegistration.status == 'approved',
                Tournament.name.ilike(f'%{category}%')
            ).distinct()
    else:
        # Default: show VALORANT teams with approved registrations
        teams_query = Team.query.join(TournamentRegistration).filter(
            TournamentRegistration.status == 'approved',
            Team.game_name.ilike('VALORANT')
        )

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

    # Pagination
    page = request.args.get('page', 1, type=int)
    teams_pagination = teams_query.paginate(page=page, per_page=10, error_out=False)
    teams = teams_pagination.items

    # Update rankings for the current filtered set, only for approved registrations
    if category != 'VALORANT':
        # Rank within the filtered teams with approved registrations
        ranked_teams = Team.query.join(TournamentRegistration).join(Tournament).filter(
            TournamentRegistration.status == 'approved',
            Tournament.name.ilike(f'%{category}%')
        ).distinct().order_by(Team.points.desc(), Team.wins.desc()).all()
    else:
        # Global rankings for teams with approved registrations
        ranked_teams = Team.query.join(TournamentRegistration).filter(
            TournamentRegistration.status == 'approved'
        ).distinct().order_by(Team.points.desc(), Team.wins.desc()).all()

    for i, team in enumerate(ranked_teams, 1):
        team.rank = i
    db.session.commit()

    # Get all upcoming tournaments with pagination
    # pylint: disable=E1102
    tournament_page = request.args.get('tournament_page', 1, type=int)
    upcoming_tournaments_query = Tournament.query.filter(
        Tournament.date >= func.now(),
        Tournament.archived == False,
        Tournament.hide == False
    ).order_by(Tournament.date.asc())
    tournaments_pagination = upcoming_tournaments_query.paginate(page=tournament_page, per_page=5, error_out=False)
    upcoming_tournaments = tournaments_pagination.items

    # Get available categories from tournament game_names
    categories = db.session.query(Tournament.game_name).distinct().all()  # type: ignore[call-arg]
    categories = [cat[0] for cat in categories]

    return render_template(
        "home.html",
        teams=teams,
        tournaments=upcoming_tournaments,
        current_category=category,
        categories=categories,
        sort_by=sort_by,
        order=order,
        pagination=teams_pagination,
        tournament_pagination=tournaments_pagination
    )



@views.route('/register-team', methods=['POST'])
@login_required
def register_team():
    """Redirect to team creation with predefined game_name from tournament."""
    if current_user.is_admin:
        flash('Admins cannot create or register teams!', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        tournament_location = request.form.get('tournamentLocation')

        tournament = Tournament.query.filter_by(
            location=tournament_location,
        ).filter(Tournament.archived == False).order_by(Tournament.date.desc()).first()

        if tournament:
            return redirect(url_for('views.team_create', game_name=tournament.game_name, tournament_location=tournament.location))
        else:
            flash('Tournament not found!', category='error')
            return redirect(url_for('views.home'))
    # Ensure the view always returns a Response for static type-checkers
    return redirect(url_for('views.home'))

@views.route('/tournament-register/<location>', methods=['POST'])
@login_required
def tournament_register(location):
    """Handle tournament registration."""
    if current_user.is_admin:
        flash('Admins cannot create or register teams!', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        team = Team.query.filter_by(captain_id=current_user.id).first()

        if not team:
            flash('You need to register a team first!', category='error')
            return redirect(url_for('views.home'))

        tournament = Tournament.query.filter_by(
            location=location,
        ).filter(Tournament.archived == False, Tournament.hide == False).order_by(Tournament.date.desc()).first()

        if not tournament:
            flash('No upcoming tournament found for this location!', category='error')
            return redirect(url_for('views.home'))

        # Validate game_name match
        if team.game_name != tournament.game_name:
            flash(f'Cannot register for this tournament! Team game ({team.game_name}) does not match tournament game ({tournament.game_name}).', category='error')
            return redirect(url_for('views.home'))

        # Check if team is eligible to join (not approved in any active tournament)
        active_approved_reg = TournamentRegistration.query.join(Tournament).filter(
            TournamentRegistration.team_id == team.id,
            TournamentRegistration.status == 'approved',
            Tournament.archived == False,
            Tournament.hide == False,
            Tournament.date >= func.now()
        ).first()

        if active_approved_reg:
            flash('Your team is already approved for an active tournament. You cannot join another until it is archived.', category='error')
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
        registration = TournamentRegistration()
        registration.tournament_id = tournament.id
        registration.team_id = team.id

        db.session.add(registration)
        db.session.commit()

        flash('Successfully registered for the tournament!', category='success')
        return redirect(url_for('views.home'))
    else:
        return redirect(url_for('views.home'))

@views.route('/tournament-join/<location>', methods=['GET', 'POST'])
@login_required
def tournament_join(location):
    """Allow user to join a tournament with an existing team."""
    if current_user.is_admin:
        flash('Admins cannot join tournaments!', category='error')
        return redirect(url_for('views.home'))

    tournament = Tournament.query.filter_by(
        location=location,
    ).filter(Tournament.archived == False).order_by(Tournament.date.desc()).first()

    if not tournament:
        flash('No upcoming tournament found for this location!', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        team_id = request.form.get('team_id')
        if not team_id:
            flash('Please select a team!', category='error')
            return redirect(url_for('views.tournament_join', location=location))

        team = Team.query.filter_by(id=team_id, captain_id=current_user.id).first()
        if not team:
            flash('Invalid team selected!', category='error')
            return redirect(url_for('views.tournament_join', location=location))

        # Validate game_name match
        if team.game_name != tournament.game_name:
            flash(f'Cannot join this tournament! Team game ({team.game_name}) does not match tournament game ({tournament.game_name}).', category='error')
            return redirect(url_for('views.tournament_join', location=location))

        # Check if team is eligible to join (not approved in any active tournament)
        active_approved_reg = TournamentRegistration.query.join(Tournament).filter(
            TournamentRegistration.team_id == team.id,
            TournamentRegistration.status == 'approved',
            Tournament.archived == False,
            Tournament.hide == False,
            Tournament.date >= func.now()
        ).first()

        if active_approved_reg:
            flash('This team is already approved for an active tournament. You cannot join another until it is archived.', category='error')
            return redirect(url_for('views.tournament_join', location=location))

        # Check if already registered
        existing_reg = TournamentRegistration.query.filter_by(
            tournament_id=tournament.id,
            team_id=team.id
        ).first()

        if existing_reg:
            flash('This team is already registered for this tournament!', category='error')
            return redirect(url_for('views.tournament_join', location=location))

        # Register for tournament
        registration = TournamentRegistration()
        registration.tournament_id = tournament.id
        registration.team_id = team.id

        db.session.add(registration)
        db.session.commit()

        flash('Successfully joined the tournament with your existing team!', category='success')
        return redirect(url_for('views.home'))

    # GET: Show form to select team
    # Get user's teams that are eligible (not approved in any active tournament)
    eligible_teams = []
    user_teams = Team.query.filter_by(captain_id=current_user.id).all()
    for team in user_teams:
        active_approved_reg = TournamentRegistration.query.join(Tournament).filter(
            TournamentRegistration.team_id == team.id,
            TournamentRegistration.status == 'approved',
            Tournament.archived == False,
            Tournament.hide == False,
            Tournament.date >= func.now()
        ).first()
        if not active_approved_reg and team.game_name == tournament.game_name:
            eligible_teams.append(team)

    return render_template('tournament_join.html', tournament=tournament, eligible_teams=eligible_teams)

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

    # Check for registration status notifications
    registrations = TournamentRegistration.query.filter_by(team_id=team_id).all()
    for reg in registrations:
        if reg.status == 'approved':
            flash(f'Your team registration for {reg.tournament.name} has been approved!', category='success')
        elif reg.status == 'rejected':
            flash(f'Your team registration for {reg.tournament.name} has been rejected!', category='error')

    return render_template('team_detail.html', team=team)

@views.route('/team/create', methods=['GET', 'POST'])
@login_required
def team_create():
    """Create a new team with players based on tournament requirements."""
    if current_user.is_admin:
        flash('Admins cannot create or register teams!', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        team_name = request.form.get('name')
        game_name = request.form.get('game_name')
        captain_phone = request.form.get('captain_phone')
        tournament_location = request.form.get('tournament_location')
        max_players = int(request.form.get('max_players', 5))  # Default to 5 if not provided

        # Handle image upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Validate file type and size
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join('website', 'static', 'uploads', 'teams')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    image_path = f'uploads/teams/{filename}'
                else:
                    flash('Invalid image file type. Only PNG, JPG, JPEG, and GIF are allowed.', category='error')
                    return redirect(url_for('views.team_create'))

        # Validate required fields
        if not game_name or game_name.strip() == '':
            flash('Please select a game for the team!', category='error')
            return redirect(url_for('views.team_create'))

        # Check if a team with this name already exists (case-insensitive)
        existing_team = Team.query.filter(Team.name.ilike(team_name)).first()

        if existing_team:
            if existing_team.captain_id == current_user.id:
                # ✅ Same user, same team — reuse it
                flash('This team already exists under your account. Redirecting to existing team.', category='info')
                return redirect(url_for('views.team_detail', team_id=existing_team.id))
            else:
                # 🚫 Another user already owns this team name
                flash('Team name already exists under another account!', category='error')
                return redirect(url_for('views.team_create'))
        else:
            # 🆕 Create a new team if it doesn't exist
            new_team = Team()
            new_team.name = team_name
            new_team.game_name = game_name.strip()
            new_team.captain_id = current_user.id
            new_team.captain_phone = captain_phone
            new_team.image = image_path
            db.session.add(new_team)
            db.session.commit()

            # Collect player names and images
            players = []
            for i in range(1, max_players + 1):
                player_name = request.form.get(f'player{i}')
                if not player_name or player_name.strip() == '':
                    flash(f'Player {i} name is required!', category='error')
                    return redirect(url_for('views.team_create'))
                players.append(player_name.strip())

            # Add players to the team
            for player_name in players:
                new_player = Player()
                new_player.name = player_name
                new_player.team = new_team
                db.session.add(new_player)
            db.session.commit()

            # Handle player image uploads
            for i in range(1, max_players + 1):
                player_image_key = f'player{i}_image'
                if player_image_key in request.files:
                    file = request.files[player_image_key]
                    if file and file.filename:
                        # Validate file type
                        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                        if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                            filename = secure_filename(file.filename)
                            upload_dir = os.path.join('website', 'static', 'uploads', 'players')
                            os.makedirs(upload_dir, exist_ok=True)
                            file_path = os.path.join(upload_dir, filename)
                            file.save(file_path)
                            # Find the player and assign the image
                            player = Player.query.filter_by(team_id=new_team.id, name=players[i-1]).first()
                            if player:
                                player.image = f'uploads/players/{filename}'
                        else:
                            flash(f'Invalid image file type for Player {i}. Only PNG, JPG, JPEG, and GIF are allowed.', category='error')
            db.session.commit()

            # If tournament_location is provided, register for the tournament
            if tournament_location:
                tournament = Tournament.query.filter_by(
                    location=tournament_location,
                ).filter(Tournament.archived == False).order_by(Tournament.date.desc()).first()
                if tournament and tournament.game_name == new_team.game_name:
                    registration = TournamentRegistration()
                    registration.tournament_id = tournament.id
                    registration.team_id = new_team.id
                    db.session.add(registration)
                    db.session.commit()
                    flash(f'Team created with {max_players} players and registered for tournament successfully!', category='success')
                else:
                    flash(f'Team created with {max_players} players successfully! (Tournament registration failed - game mismatch)', category='warning')
            else:
                flash(f'Team created with {max_players} players successfully!', category='success')

            return redirect(url_for('views.teams'))

    # Get available categories from tournament game_names
    categories = db.session.query(Tournament.game_name).distinct().all()  # type: ignore[call-arg]
    categories = [cat[0] for cat in categories]

    # Check for predefined game_name from URL params
    predefined_game_name = request.args.get('game_name')
    predefined_tournament_location = request.args.get('tournament_location')

    # Determine max_players
    max_players = 5  # Default
    if predefined_tournament_location:
        tournament = Tournament.query.filter_by(
            location=predefined_tournament_location,
        ).filter(Tournament.archived == False).order_by(Tournament.date.desc()).first()
        if tournament:
            max_players = tournament.max_players

    return render_template(
        'team_form.html',
        action='Create',
        categories=categories,
        predefined_game_name=predefined_game_name,
        predefined_tournament_location=predefined_tournament_location,
        max_players=max_players
    )

@views.route('/team/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def team_edit(team_id):
    """Edit a team's details."""
    team = Team.query.get_or_404(team_id)
    if team.captain_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        team_name = request.form.get('name')
        game_name = request.form.get('game_name')
        captain_phone = request.form.get('captain_phone')

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Validate file type and size
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join('website', 'static', 'uploads', 'teams')
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
                    team.image = f'uploads/teams/{filename}'
                else:
                    flash('Invalid image file type. Only PNG, JPG, JPEG, and GIF are allowed.', category='error')
                    return redirect(url_for('views.team_edit', team_id=team_id))

        # Validate required fields
        if not game_name or game_name.strip() == '':
            flash('Please select a game for the team!', category='error')
            return redirect(url_for('views.team_edit', team_id=team_id))

        if Team.query.filter(Team.name.ilike(team_name), Team.id != team_id).first():
            flash('Team name already exists!', category='error')
            return redirect(url_for('views.team_edit', team_id=team_id))

        team.name = team_name
        team.game_name = game_name.strip()
        team.captain_phone = captain_phone

        # Update player names and images
        max_players = len(team.players)
        for i in range(1, max_players + 1):
            player_name = request.form.get(f'player{i}')
            if player_name and player_name.strip():
                player = team.players[i-1] if i-1 < len(team.players) else None
                if player:
                    player.name = player_name.strip()

            # Handle player image uploads
            player_image_key = f'player{i}_image'
            if player_image_key in request.files:
                file = request.files[player_image_key]
                if file and file.filename:
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                        filename = secure_filename(file.filename)
                        upload_dir = os.path.join('website', 'static', 'uploads', 'players')
                        os.makedirs(upload_dir, exist_ok=True)
                        file_path = os.path.join(upload_dir, filename)
                        file.save(file_path)
                        # Update the player's image
                        player = team.players[i-1] if i-1 < len(team.players) else None
                        if player:
                            player.image = f'uploads/players/{filename}'
                    else:
                        flash(f'Invalid image file type for Player {i}. Only PNG, JPG, JPEG, and GIF are allowed.', category='error')
                        return redirect(url_for('views.team_edit', team_id=team_id))

        db.session.commit()
        flash('Team updated successfully!', category='success')
        return redirect(url_for('views.team_detail', team_id=team_id))

    # Get available categories from tournament game_names
    categories = db.session.query(Tournament.game_name).distinct().all()  # type: ignore[call-arg]
    categories = [cat[0] for cat in categories]

    return render_template(
        'team_form.html',
        action='Edit',
        team=team,
        categories=categories,
        max_players=len(team.players)
    )

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

@views.route('/player/<int:player_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_player(player_id):
    """Edit a player's name."""
    player = Player.query.get_or_404(player_id)
    if player.team.captain_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        # Check if it's an AJAX request (JSON content type)
        if request.is_json:
            data = request.get_json()
            new_name = data.get('name', '').strip()
            if not new_name:
                return {'success': False, 'message': 'Player name cannot be empty.'}, 400

            player.name = new_name
            db.session.commit()
            return {'success': True, 'new_name': new_name}

        # Original form-based submission
        player.name = request.form.get('name')
        db.session.commit()
        flash('Player updated successfully!', category='success')
        return redirect(url_for('views.team_detail', team_id=player.team_id))

    return render_template('player_form.html', player=player, action='Edit')



# CRUD for Tournaments (assuming admin access, for simplicity all logged-in users can manage for now)

@views.route('/tournaments')
@login_required
@admin_required
def tournaments():
    """List all tournaments."""
    page = request.args.get('page', 1, type=int)
    tournaments_query = Tournament.query.filter_by(archived=False)
    tournaments_pagination = tournaments_query.paginate(page=page, per_page=10, error_out=False)
    tournaments = tournaments_pagination.items
    return render_template('tournament_list.html', tournaments=tournaments, pagination=tournaments_pagination)

@views.route('/tournament/create', methods=['GET', 'POST'])
@login_required
@admin_required
def tournament_create():
    """Create a new tournament."""
    if request.method == 'POST':
        name = request.form.get('name')
        game_name = request.form.get('game_name')
        location = request.form.get('location')
        date_str = request.form.get('date')
        max_players_str = request.form.get('max_players')

        # Validate date is present
        if not date_str or date_str.strip() == '':
            flash('Please enter the date of the event!', category='error')
            return redirect(url_for('views.tournament_create'))

        # Parse and validate date
        try:
            tournament_date = datetime.fromisoformat(date_str.replace('T', ' '))
        except ValueError:
            flash('Invalid date format!', category='error')
            return redirect(url_for('views.tournament_create'))

        # Check if date is in the past
        if tournament_date < datetime.now():
            flash('Please enter a future date!', category='error')
            return redirect(url_for('views.tournament_create'))

        if not max_players_str:
            flash('Max players is required!', category='error')
            return redirect(url_for('views.tournament_create'))

        try:
            max_players = int(max_players_str)
        except ValueError:
            flash('Max players must be a number!', category='error')
            return redirect(url_for('views.tournament_create'))

        new_tournament = Tournament()
        new_tournament.name = name
        new_tournament.game_name = game_name
        new_tournament.location = location
        new_tournament.date = tournament_date
        new_tournament.max_players = max_players
        db.session.add(new_tournament)
        db.session.commit()
        flash('Tournament created successfully!', category='success')
        return redirect(url_for('views.tournaments'))

    return render_template('tournament_form.html', action='Create')

@views.route('/tournament/<int:tournament_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def tournament_edit(tournament_id):
    """Edit an existing tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)

    if request.method == 'POST':
        name = request.form.get('name')
        game_name = request.form.get('game_name')
        location = request.form.get('location')
        date_str = request.form.get('date')
        max_players_str = request.form.get('max_players')

        # Validate date is present
        if not date_str or date_str.strip() == '':
            flash('Please enter the date of the event!', category='error')
            return redirect(url_for('views.tournament_edit', tournament_id=tournament_id))

        # Parse and validate date
        try:
            tournament_date = datetime.fromisoformat(date_str.replace('T', ' '))
        except ValueError:
            flash('Invalid date format!', category='error')
            return redirect(url_for('views.tournament_edit', tournament_id=tournament_id))

        # Check if date is in the past
        if tournament_date < datetime.now():
            flash(' Please enter a future date!', category='error')
            return redirect(url_for('views.tournament_edit', tournament_id=tournament_id))

        if not max_players_str:
            flash('Max players is required!', category='error')
            return redirect(url_for('views.tournament_edit', tournament_id=tournament_id))

        try:
            max_players = int(max_players_str)
        except ValueError:
            flash('Max players must be a number!', category='error')
            return redirect(url_for('views.tournament_edit', tournament_id=tournament_id))

        tournament.name = name
        tournament.game_name = game_name
        tournament.location = location
        tournament.date = tournament_date
        tournament.max_players = max_players
        db.session.commit()
        flash('Tournament updated successfully!', category='success')
        return redirect(url_for('views.tournaments'))

    return render_template('tournament_form.html', tournament=tournament, action='Edit')

@views.route('/tournament/<int:tournament_id>/archive', methods=['POST'])
@login_required
@admin_required
def tournament_archive(tournament_id):
    """Archive a tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)

    # Set all approved registrations for this tournament to 'archived'
    approved_regs = TournamentRegistration.query.filter_by(tournament_id=tournament_id, status='approved').all()
    for reg in approved_regs:
        reg.status = 'archived'

    tournament.archived = True
    db.session.commit()

    # Log the manual archiving
    audit_log = AuditLog(
        user_id=current_user.id,
        action='archive_tournament',
        target_type='tournament',
        target_id=tournament_id,
        details=json.dumps({
            'tournament_name': tournament.name,
            'location': tournament.location
        })
    )
    db.session.add(audit_log)
    db.session.commit()

    flash('Tournament archived successfully!', category='success')
    return redirect(url_for('views.tournaments'))

@views.route('/api/tournament/<location>')
def api_tournament_details(location):
    """API endpoint to get tournament details by location."""
    # pylint: disable=E1102
    tournament = Tournament.query.filter(
        Tournament.location == location,
        Tournament.date >= func.now(),
        Tournament.archived == False,
        Tournament.game_name.in_(['VALORANT', 'CS2'])
    ).order_by(Tournament.date.desc()).first()
    if tournament:
        return {'game_name': tournament.game_name, 'name': tournament.name}
    return {'error': 'Tournament not found'}, 404

@views.route('/tournament/<int:tournament_id>/registrations')
@login_required
def tournament_registrations(tournament_id):
    """View registrations for a tournament."""
    tournament = Tournament.query.get_or_404(tournament_id)
    registrations = TournamentRegistration.query.filter_by(tournament_id=tournament_id).all()
    return render_template('tournament_registrations.html', tournament=tournament, registrations=registrations)

@views.route('/approve_registration/<int:reg_id>', methods=['POST'])
@login_required
@admin_required
def approve_registration(reg_id):
    """Approve a tournament registration."""
    registration = TournamentRegistration.query.get_or_404(reg_id)
    registration.status = 'approved'
    db.session.commit()

    # Log the approval
    audit_log = AuditLog(
        user_id=current_user.id,
        action='approve_registration',
        target_type='registration',
        target_id=reg_id,
        details=json.dumps({
            'team_name': registration.team.name,
            'tournament_name': registration.tournament.name
        })
    )
    db.session.add(audit_log)
    db.session.commit()

    flash(f'Registration for {registration.team.name} has been approved!', category='success')
    return redirect(url_for('views.tournament_registrations', tournament_id=registration.tournament_id))

@views.route('/reject_registration/<int:reg_id>', methods=['POST'])
@login_required
@admin_required
def reject_registration(reg_id):
    """Reject a tournament registration."""
    registration = TournamentRegistration.query.get_or_404(reg_id)
    registration.status = 'rejected'
    db.session.commit()

    # Log the rejection
    audit_log = AuditLog(
        user_id=current_user.id,
        action='reject_registration',
        target_type='registration',
        target_id=reg_id,
        details=json.dumps({
            'team_name': registration.team.name,
            'tournament_name': registration.tournament.name
        })
    )
    db.session.add(audit_log)
    db.session.commit()

    flash(f'Registration for {registration.team.name} has been rejected!', category='error')
    return redirect(url_for('views.tournament_registrations', tournament_id=registration.tournament_id))

# Admin Rankings Management

@views.route('/manage-rankings')
@login_required
@admin_required
def manage_rankings():
    """Admin page to manage team rankings."""
    # Get teams that have approved tournament registrations
    page = request.args.get('page', 1, type=int)
    teams_query = Team.query.join(TournamentRegistration).filter(
        TournamentRegistration.status == 'approved'
    ).distinct()
    teams_pagination = teams_query.paginate(page=page, per_page=10, error_out=False)
    teams = teams_pagination.items
    return render_template('manage_rankings.html', teams=teams, pagination=teams_pagination)

@views.route('/manage-rankings/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_ranking(team_id):
    """Edit points and wins for a team."""
    team = Team.query.get_or_404(team_id)

    if request.method == 'POST':
        points_str = request.form.get('points')
        wins_str = request.form.get('wins')

        if not points_str or not wins_str:
            flash('Points and wins are required!', category='error')
            return redirect(url_for('views.edit_ranking', team_id=team_id))

        try:
            points = int(points_str)
            wins = int(wins_str)
        except ValueError:
            flash('Points and wins must be numbers!', category='error')
            return redirect(url_for('views.edit_ranking', team_id=team_id))

        # Capture old values
        old_points = team.points
        old_wins = team.wins

        team.points = points
        team.wins = wins
        db.session.commit()

        # Log the points/wins changes
        audit_log = AuditLog(
            user_id=current_user.id,
            action='edit_ranking',
            target_type='team',
            target_id=team_id,
            details=json.dumps({
                'team_name': team.name,
                'old_points': old_points,
                'new_points': points,
                'old_wins': old_wins,
                'new_wins': wins
            })
        )
        db.session.add(audit_log)
        db.session.commit()

        flash('Ranking updated successfully!', category='success')
        return redirect(url_for('views.manage_rankings'))

    return render_template('edit_ranking.html', team=team)

@views.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """View audit logs."""
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Show 50 logs per page

    # Get all audit logs, ordered by timestamp descending
    logs_query = AuditLog.query.order_by(AuditLog.timestamp.desc())
    logs_pagination = logs_query.paginate(page=page, per_page=per_page, error_out=False)
    logs = logs_pagination.items

    return render_template('audit_logs.html', logs=logs, pagination=logs_pagination)

@views.route('/export-audit-logs')
@login_required
@admin_required
def export_audit_logs():
    """Export audit logs to PDF."""
    # Get all audit logs
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Title style
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )

    # Header style
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold'
    )

    # Cell style
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=8
    )

    # Build PDF content
    content = []

    # Title
    title = Paragraph("Audit Logs Report", title_style)
    content.append(title)
    content.append(Spacer(1, 12))

    # Table data
    data = [
        [Paragraph('Timestamp', header_style), Paragraph('User', header_style), Paragraph('Action', header_style), Paragraph('Target Type', header_style), Paragraph('Target ID', header_style), Paragraph('Details', header_style)]
    ]

    for log in logs:
        user_email = log.user.email if log.user else 'System (Auto)'
        action = log.action.replace('_', ' ').title()
        target_type = log.target_type.title()
        timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        # Truncate details if too long
        details = log.details if log.details else 'No details'
        if len(details) > 100:
            details = details[:97] + '...'

        data.append([
            Paragraph(timestamp, cell_style),
            Paragraph(user_email, cell_style),
            Paragraph(action, cell_style),
            Paragraph(target_type, cell_style),
            Paragraph(str(log.target_id), cell_style),
            Paragraph(details, cell_style)
        ])

    # Create table
    table = Table(data, colWidths=[70, 70, 60, 60, 40, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))

    content.append(table)

    # Build PDF
    doc.build(content)

    # Return PDF response
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=audit_logs.pdf'
    return response
