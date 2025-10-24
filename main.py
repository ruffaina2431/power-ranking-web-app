"""
Main Entry Point - E-Sports Tournament Hub

This module serves as the entry point for the E-Sports Tournament Hub web application.
It initializes the Flask application using the factory pattern and runs the development server.

Application Features:
1. User Management
   - Registration and authentication
   - Secure password handling
   - Session management

2. Team System
   - Team creation and management
   - Player roster handling
   - Team statistics tracking
   - Power rankings

3. Tournament System
   - Tournament creation
   - Team registration
   - Multiple venue support (Point A/B)
   - Registration status tracking

4. Game Categories
   - Multiple game support
   - Category-based filtering
   - Search functionality

Technical Details:
- Uses Flask framework
- SQLAlchemy for database
- Flask-Login for authentication
- Bootstrap for frontend
- jQuery for dynamic interactions

Flow:
1. Application factory called
2. Database initialized
3. Blueprints registered
4. Server started in debug mode

Note: Debug mode is enabled for development purposes.
      Disable debug mode in production deployment.
"""

from website import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run the application in debug mode for development
    # Debug mode enables auto-reload and detailed error pages
    app.run(debug=True)
