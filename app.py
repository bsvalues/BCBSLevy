"""
Web Scraper Application - Simple Flask web app with Trafilatura integration.

This application allows users to extract clean text content from websites
using the Trafilatura library.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import trafilatura

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In-memory storage for scraped content
# In a production app, this would use a database
scraped_content = {}

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
        
        request_id = str(datetime.now().timestamp())
        scraped_content[request_id] = {
            'url': url,
            'status': 'processing',
            'created_at': datetime.now(),
            'content': None,
            'completed_at': None,
            'error': None
        }
        
        try:
            # Scrape the website using trafilatura
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                raise Exception(f"Failed to download content from {url}")
                
            content = trafilatura.extract(downloaded)
            
            if not content:
                raise Exception(f"No content could be extracted from {url}")
            
            # Save the results
            scraped_content[request_id]['status'] = 'completed'
            scraped_content[request_id]['content'] = content
            scraped_content[request_id]['completed_at'] = datetime.now()
            
            flash('Content successfully scraped!', 'success')
            return redirect(url_for('results', request_id=request_id))
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            scraped_content[request_id]['status'] = 'failed'
            scraped_content[request_id]['error'] = str(e)
            
            flash(f'Failed to scrape content: {str(e)}', 'danger')
            return redirect(url_for('scrape'))
    
    # GET request - show form with recent requests
    recent_requests = []
    for req_id, data in scraped_content.items():
        recent_requests.append({
            'id': req_id,
            'url': data['url'],
            'status': data['status'],
            'created_at': data['created_at']
        })
    
    # Sort by creation date (newest first) and limit to 5
    recent_requests = sorted(
        recent_requests, 
        key=lambda x: x['created_at'], 
        reverse=True
    )[:5]
    
    return render_template('scrape.html', recent_requests=recent_requests)

@app.route('/results/<request_id>')
def results(request_id):
    """Show the results of a scrape request."""
    if request_id not in scraped_content:
        flash('Scrape request not found.', 'danger')
        return redirect(url_for('scrape'))
    
    return render_template('results.html', 
                           scrape_request=scraped_content[request_id], 
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