"""
Web Scraper Application - Primary entry point.

This module serves as the primary entry point for running the Flask
application with Gunicorn, as well as for direct execution with
the Flask development server.
"""

import os
import logging

# Import the app from app.py
from app import app

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Note: Health check route is now defined in app.py

# This makes the app discoverable by Gunicorn
# Do not modify this section - Gunicorn looks for app in this location

# Run the application when executing the script directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)