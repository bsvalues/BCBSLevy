"""
WSGI module for the Levy Calculation Application.

This module is used by the WSGI server (e.g., Gunicorn) to run the application.
It uses the main Flask application instance from app.py which contains
all the necessary route registrations and configuration.
"""
from app import app

# Import additional blueprints if needed
# Note: Most blueprints are already registered in app.py

# Create a reference to the application for WSGI servers
# This is standardized to use the main app.py application instance

# WSGI app
application = app

# For local testing
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)