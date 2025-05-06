"""
Web Scraper Application - Routes module.

This module defines the routes for the web scraping application.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db
from models import ScrapeRequest, ScrapedContent
from web_scraper import get_website_text_content

# Create a Blueprint for the main routes
main_bp = Blueprint('main', __name__)

# Template filters
@main_bp.app_template_filter('nl2br')
def nl2br(value):
    """Convert newlines to <br> tags."""
    if not value:
        return ''
    return value.replace('\n', '<br>')


@main_bp.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')


@main_bp.route('/scrape', methods=['GET', 'POST'])
def scrape():
    """Handle scraping requests."""
    if request.method == 'POST':
        url = request.form.get('url')
        
        if not url:
            flash('Please provide a URL to scrape.', 'danger')
            return redirect(url_for('main.scrape'))
        
        # Create a new scrape request
        scrape_request = ScrapeRequest(
            url=url,
            status='processing'
        )
        db.session.add(scrape_request)
        db.session.commit()
        
        try:
            # Perform the scraping
            content = get_website_text_content(url)
            
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
            return redirect(url_for('main.results', request_id=scrape_request.id))
            
        except Exception as e:
            # Update the scrape request with error details
            scrape_request.status = 'failed'
            scrape_request.error_message = str(e)
            db.session.commit()
            
            flash(f'Failed to scrape content: {str(e)}', 'danger')
            return redirect(url_for('main.scrape'))
    
    # GET request - show the form
    recent_requests = ScrapeRequest.query.order_by(ScrapeRequest.created_at.desc()).limit(5).all()
    return render_template('scrape.html', recent_requests=recent_requests)


@main_bp.route('/results/<int:request_id>')
def results(request_id):
    """Show the results of a scrape request."""
    scrape_request = ScrapeRequest.query.get_or_404(request_id)
    
    return render_template('results.html', scrape_request=scrape_request)


@main_bp.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint for scraping a URL."""
    data = request.json
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    
    # Create a new scrape request
    scrape_request = ScrapeRequest(
        url=url,
        status='processing'
    )
    db.session.add(scrape_request)
    db.session.commit()
    
    try:
        # Perform the scraping
        content = get_website_text_content(url)
        
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
        
        return jsonify({
            'request_id': scrape_request.id,
            'status': 'completed',
            'content': content[:500] + '...' if len(content) > 500 else content
        }), 200
        
    except Exception as e:
        # Update the scrape request with error details
        scrape_request.status = 'failed'
        scrape_request.error_message = str(e)
        db.session.commit()
        
        return jsonify({
            'request_id': scrape_request.id,
            'status': 'failed',
            'error': str(e)
        }), 500