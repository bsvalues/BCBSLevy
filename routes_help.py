"""
Routes for the contextual help system.

These routes handle API requests for contextual help explanations
and AI-powered guidance throughout the TerraFusion platform.
"""
import json
import logging
from flask import Blueprint, jsonify, request, render_template, url_for
from flask_login import current_user, login_required

import contextual_help_service as help_service

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Blueprint
help_bp = Blueprint('help', __name__, url_prefix='/api/help')

@help_bp.route('/topics', methods=['GET'])
def get_help_topics():
    """Return all available help topics with metadata."""
    topics = help_service.get_help_topics()
    
    # Add category grouping
    categories = {}
    for topic_id, topic_data in topics.items():
        category = topic_data.get('category', 'other')
        if category not in categories:
            categories[category] = []
        
        categories[category].append({
            'id': topic_id,
            'title': topic_data['title'],
            'short_desc': topic_data['short_desc']
        })
    
    return jsonify({
        'success': True,
        'topics': topics,
        'categories': categories
    })

@help_bp.route('/explain/<topic_id>', methods=['GET'])
def get_explanation(topic_id):
    """Generate and return an explanation for a specific topic."""
    context = request.args.get('context')
    user_role = 'administrator' if current_user.is_authenticated and getattr(current_user, 'is_admin', False) else 'analyst'
    
    # Get additional info from request if provided
    additional_info = {}
    if request.args.get('additional_info'):
        try:
            additional_info = json.loads(request.args.get('additional_info'))
        except:
            logger.warning("Failed to parse additional_info parameter as JSON")
    
    # Generate the explanation
    explanation = help_service.generate_explanation(
        topic_id, 
        context=context, 
        additional_info=additional_info,
        user_role=user_role
    )
    
    return jsonify({
        'success': True,
        'explanation': explanation
    })

@help_bp.route('/chart/<chart_type>', methods=['POST'])
def get_chart_explanation(chart_type):
    """Generate and return an explanation for a data visualization chart."""
    data = request.json or {}
    data_context = data.get('data_context', {})
    user_role = 'administrator' if current_user.is_authenticated and getattr(current_user, 'is_admin', False) else 'analyst'
    
    # Generate the chart explanation
    explanation = help_service.get_explanation_for_chart(
        chart_type,
        data_context=data_context,
        user_role=user_role
    )
    
    return jsonify({
        'success': True,
        'explanation': explanation
    })

@help_bp.route('/bulk', methods=['POST'])
def get_bulk_explanations():
    """Generate and return explanations for multiple topics."""
    data = request.json or {}
    topic_ids = data.get('topic_ids', [])
    context = data.get('context')
    user_role = 'administrator' if current_user.is_authenticated and getattr(current_user, 'is_admin', False) else 'analyst'
    
    if not topic_ids:
        return jsonify({
            'success': False,
            'error': 'No topic_ids provided'
        }), 400
    
    # Generate bulk explanations
    explanations = help_service.get_bulk_explanations(
        topic_ids,
        context=context,
        user_role=user_role
    )
    
    return jsonify({
        'success': True,
        'explanations': explanations
    })

@help_bp.route('/popup/<topic_id>', methods=['GET'])
def render_help_popup(topic_id):
    """Render a standalone help popup for the given topic."""
    context = request.args.get('context')
    user_role = 'administrator' if current_user.is_authenticated and getattr(current_user, 'is_admin', False) else 'analyst'
    
    # Generate the explanation
    explanation = help_service.generate_explanation(
        topic_id, 
        context=context,
        user_role=user_role
    )
    
    # Render the popup template
    return render_template(
        'help/popup.html',
        topic_id=topic_id,
        explanation=explanation
    )

# Web routes (not API)
web_help_bp = Blueprint('web_help', __name__, url_prefix='/help')

@web_help_bp.route('/example', methods=['GET'])
def example_page():
    """Show an example page with contextual help implementation."""
    return render_template('help/example_usage.html')

def init_app(app):
    """Initialize the help routes with the Flask app."""
    app.register_blueprint(help_bp)
    app.register_blueprint(web_help_bp)
    logger.info("Help routes initialized")
    return help_bp