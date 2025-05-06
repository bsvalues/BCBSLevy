"""
TerraLevy Application (Levy Calculation System) - Primary entry point.

This module serves as the primary entry point for running the Flask application,
making the app discoverable by Gunicorn WSGI server.
"""

import os
import logging
from app import app  # Import the Flask app from app.py

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This makes the app discoverable by Gunicorn
# Do not modify this section - Gunicorn looks for app in this location

# Run the application when executing the script directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)