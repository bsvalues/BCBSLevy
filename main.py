"""
PRODUCTION ENTRY POINT for the LevyMaster application.

This module serves as the primary entry point for running the Flask
application in production with Gunicorn, as well as for direct execution
with the Flask development server.

This file provides:
1. The 'app' object that Gunicorn looks for when starting the server
2. Basic logging configuration
3. Proper host/port binding for development server execution

NOTE: This file imports from app.py, which is the authoritative source
for all application configuration, blueprints, and route registration.
"""

import os
import logging

from app import app

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Log that application is being served
app.logger.info("Starting LevyMaster application")

# This makes the app discoverable by Gunicorn
# Do not modify this section - Gunicorn looks for app in this location

# Run the application when executing the script directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)