"""
Website package initialization for E-Sports Tournament Hub.

This module initializes the Flask application and configures all necessary components
including database, authentication, and blueprints for the e-sports tournament management system.

Components configured:
- Flask-SQLAlchemy for database operations
- Flask-Login for user session management
- Authentication and views blueprints
- Database models and table creation
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

# Initialize SQLAlchemy instance without binding it to an app yet
db = SQLAlchemy()
DB_NAME = "esports_tournament"

def create_app():
    """
    Application factory function.
    
    Creates and configures the Flask application instance.
    
    Returns:
        Flask: The configured Flask application instance.
    """
    # Initialize Flask application
    app = Flask(__name__)
    
    # Configure secret key and database
    app.config['SECRET_KEY'] = 'pythonwebappsecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/' + DB_NAME
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with this application
    db.init_app(app)
    
    # Import blueprints
    from .views import views
    from .auth import auth
    
    # Register blueprints with the application
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # Import models and create database tables
    from .models import User, Team, Player, Tournament, TournamentRegistration
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
    # Configure login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        from .models import User
        return User.query.get(int(id))
    
    return app
