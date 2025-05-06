"""
Simple TerraLevy Application - Minimal version for debugging.

This is a simplified version of the application for diagnosing issues.
"""

import os
import logging
from flask import Flask, render_template, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('home.html')

@app.route('/test')
def test():
    """Test route for debugging."""
    return jsonify({
        'status': 'success',
        'message': 'Simple app is working!'
    })

# Simple 404 and 500 error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 error: {str(e)}")
    return "Page not found. Please check the URL.", 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 error: {str(e)}")
    return "Internal server error. Please try again later.", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)