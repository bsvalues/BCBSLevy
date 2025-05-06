"""
Web Scraper Module - Routes for integrating with TerraLevy.

This module provides routes for the web scraper functionality that are integrated
into the main TerraLevy application.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import trafilatura
import logging

from models import db, ScrapeRequest, ScrapedContent

# Create a Blueprint for the web scraper routes
webscraper_bp = Blueprint('webscraper', __name__, url_prefix='/tools/scraper')

# Configure logging
logger = logging.getLogger(__name__)

@webscraper_bp.route('/')
def index():
    """Render the web scraper homepage."""
    return render_template('webscraper/index.html')

@webscraper_bp.route('/scrape', methods=['GET', 'POST'])
def scrape():
    """Handle scraping requests."""
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            flash('Please provide a URL to scrape.', 'danger')
            return redirect(url_for('webscraper.scrape'))
        
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
            return redirect(url_for('webscraper.results', request_id=scrape_request.id))
            
        except Exception as e:
            # Update the scrape request with error details
            scrape_request.status = 'failed'
            scrape_request.error_message = str(e)
            db.session.commit()
            
            logger.error(f"Error scraping {url}: {str(e)}")
            flash(f'Failed to scrape content: {str(e)}', 'danger')
            return redirect(url_for('webscraper.scrape'))
    
    # GET request - show form with recent requests
    recent_requests = ScrapeRequest.query.order_by(ScrapeRequest.created_at.desc()).limit(5).all()
    return render_template('webscraper/scrape.html', recent_requests=recent_requests)

@webscraper_bp.route('/results/<int:request_id>')
def results(request_id):
    """Show the results of a scrape request."""
    scrape_request = ScrapeRequest.query.get_or_404(request_id)
    
    return render_template('webscraper/results.html', 
                         scrape_request=scrape_request, 
                         request_id=request_id)

# Template filters
@webscraper_bp.app_template_filter('format_date')
def format_date(date):
    """Format a date value."""
    if date:
        return date.strftime('%Y-%m-%d %H:%M:%S')
    return ''

@webscraper_bp.app_template_filter('truncate_text')
def truncate_text(text, length=100):
    """Truncate text to specified length with ellipsis."""
    if text and len(text) > length:
        return text[:length] + '...'
    return text if text else ''

@webscraper_bp.app_template_filter('nl2br')
def nl2br(text):
    """Convert newlines to HTML line breaks."""
    if not text:
        return ''
    return text.replace('\n', '<br>')