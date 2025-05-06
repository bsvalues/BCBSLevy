"""
Web Scraper Application - Flask web app with Trafilatura integration and PostgreSQL.

This application allows users to extract clean text content from websites
using the Trafilatura library and store results in a PostgreSQL database.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import trafilatura

# Import database models
from models import db, ScrapeRequest, ScrapedContent

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the database with the app
db.init_app(app)

# Create database tables within app context if they don't exist
with app.app_context():
    db.create_all()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    """Handle scraping requests."""
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            flash('Please provide a URL to scrape.', 'danger')
            return redirect(url_for('scrape'))
        
        # Create a new scrape request
        scrape_request = ScrapeRequest(
            url=url,
            status='processing'
        )
        db.session.add(scrape_request)
        db.session.commit()
        
        try:
            # Scrape the website using trafilatura
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                raise Exception(f"Failed to download content from {url}")
                
            content = trafilatura.extract(downloaded)
            
            if not content:
                raise Exception(f"No content could be extracted from {url}")
            
            # Update the scrape request status
            scrape_request.status = 'completed'
            scrape_request.completed_at = datetime.utcnow()
            
            # Create scraped content record
            scraped_content = ScrapedContent(
                scrape_request_id=scrape_request.id,
                content=content
            )
            db.session.add(scraped_content)
            db.session.commit()
            
            flash('Content successfully scraped!', 'success')
            return redirect(url_for('results', request_id=scrape_request.id))
            
        except Exception as e:
            # Update the scrape request with error details
            scrape_request.status = 'failed'
            scrape_request.error_message = str(e)
            db.session.commit()
            
            logger.error(f"Error scraping {url}: {str(e)}")
            flash(f'Failed to scrape content: {str(e)}', 'danger')
            return redirect(url_for('scrape'))
    
    # GET request - show form with recent requests
    recent_requests = ScrapeRequest.query.order_by(ScrapeRequest.created_at.desc()).limit(5).all()
    return render_template('scrape.html', recent_requests=recent_requests)

@app.route('/results/<int:request_id>')
def results(request_id):
    """Show the results of a scrape request."""
    scrape_request = ScrapeRequest.query.get_or_404(request_id)
    
    return render_template('results.html', 
                           scrape_request=scrape_request, 
                           request_id=request_id)

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