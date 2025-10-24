"""
Authentication Blueprint for E-Sports Tournament Hub.

This module handles all authentication-related routes and functionality
including user registration, login, logout, and session management.
Provides secure password hashing and form validation for user accounts.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

# Create a Blueprint for authentication routes
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route handler.

    Methods:
        GET: Display the login form
        POST: Process the login form submission

    Returns:
        rendered template: The login page HTML template.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", boolean=True)

@auth.route('/logout')
@login_required
def logout():
    """
    Logout route handler.
    Logs out the current user and redirects to home.
    """
    logout_user()
    flash('Logged out successfully!', category='success')
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    """
    Sign-up route handler.
    
    Methods:
        GET: Display the sign-up form
        POST: Process the sign-up form submission with validation
    
    Form Validation:
        - Email must be > 3 characters
        - First name must be > 1 character
        - Passwords must match
        - Password must be ≥ 7 characters
    
    Returns:
        rendered template: The sign-up page HTML template.
    """
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        firstName = request.form.get('firstname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Validate form data
        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Check if email already exists
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists.', category='error')
            else:
                # Create new user
                new_user = User(
                    email=email,
                    first_name=firstName,
                    password=generate_password_hash(password1, method='pbkdf2:sha256')
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                return redirect(url_for('views.home'))

    return render_template("sign_up.html")
