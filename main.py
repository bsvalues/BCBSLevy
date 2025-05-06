"""
TerraLevy Application - Primary entry point.

This module serves as the primary entry point for running the Flask
application with Gunicorn, as well as for direct execution with
the Flask development server.
"""

import os
import logging
import sys

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    # Import the app from app.py
    from app import app
    logger.info("Successfully imported Flask app")
    
    # Register a basic error handler
    @app.errorhandler(404)
    def page_not_found(e):
        logger.error(f"404 error: {str(e)}")
        return "Page not found. Please check the URL or return to the homepage.", 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"500 error: {str(e)}")
        return "Internal server error. The application team has been notified.", 500
    
except Exception as e:
    logger.error(f"Failed to import Flask app: {str(e)}")
    raise

# This makes the app discoverable by Gunicorn
# Do not modify this section - Gunicorn looks for app in this location

# Run the application when executing the script directly
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 5000))
        logger.info(f"Starting Flask app on http://0.0.0.0:{port}")
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {str(e)}")
        raise