"""
TerraLevy Application - Flask web app for tax district and levy management.

This application includes tools for tax district management, forecasting, 
historical analysis, and web scraping capabilities.
"""

import os
import logging
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.info("Starting TerraLevy application")

try:
    import trafilatura
    logger.info("Trafilatura imported successfully")
except Exception as e:
    logger.error(f"Error importing trafilatura: {e}")
    
try:
    # Import database models
    from models import db, ScrapeRequest, ScrapedContent
    logger.info("Database models imported successfully")
except Exception as e:
    logger.error(f"Error importing database models: {e}")

try:
    # Import blueprints
    from routes_webscraper import webscraper_bp
    logger.info("Webscraper blueprint imported successfully")
except Exception as e:
    logger.error(f"Error importing blueprints: {e}")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
logger.info("Flask app initialized")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
logger.info("Database configured")

# Initialize the database with the app
db.init_app(app)
logger.info("Database initialized")

# Register blueprints
try:
    app.register_blueprint(webscraper_bp)
    logger.info("Webscraper blueprint registered")
except Exception as e:
    logger.error(f"Error registering blueprints: {e}")

# Create database tables within app context if they don't exist
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Main routes for TerraLevy application will go here
@app.route('/')
def index():
    """Render the TerraLevy homepage."""
    return render_template('home.html')

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {'status': 'healthy', 'service': 'web-scraper'}, 200

# Add template filters and functions
@app.template_filter('format_date')
def format_date(date):
    """Format a date value."""
    if date:
        return date.strftime('%Y-%m-%d %H:%M:%S')
    return ''

@app.template_filter('truncate_text')
def truncate_text(text, length=100):
    """Truncate text to specified length with ellipsis."""
    if text and len(text) > length:
        return text[:length] + '...'
    return text if text else ''

@app.template_filter('nl2br')
def nl2br(text):
    """Convert newlines to HTML line breaks."""
    if not text:
        return ''
    return text.replace('\n', '<br>')

# Add global template functions
@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return {'now': now}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)