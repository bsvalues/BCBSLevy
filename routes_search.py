"""
Search routes for the Levy Calculation System.

This module provides route handlers for the intelligent search functionality
with fuzzy matching and autocomplete capabilities.
"""

import logging
from typing import List, Dict, Any, Optional

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func

from utils.search_utils import (
    search_entities,
    get_autocomplete_suggestions,
    log_search_activity
)

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
search_bp = Blueprint('search', __name__, url_prefix='/search')

@search_bp.route('/', methods=['GET'])
@login_required
def search_page():
    """
    Render the search page with optional pre-executed search.
    
    Query Parameters:
        q: The search query text
        types: Comma-separated list of entity types to search
        year: Year filter for entities with year attribute
    
    Returns:
        Rendered search page with any search results
    """
    query = request.args.get('q', '')
    entity_types_param = request.args.get('types', '')
    year_param = request.args.get('year')
    
    # Parse entity types from comma-separated string
    entity_types = [t.strip() for t in entity_types_param.split(',')] if entity_types_param else None
    
    # Parse year parameter if present
    year = None
    if year_param:
        try:
            year = int(year_param)
        except ValueError:
            year = None
    
    # Get current year as default for year dropdown if none provided
    if not year:
        from datetime import datetime
        year = datetime.now().year
    
    # Initialize results
    results = {}
    result_count = 0
    
    # Execute search if query is provided
    if query:
        results = search_entities(
            query=query,
            entity_types=entity_types,
            year=year,
            limit=5,
            min_score=60
        )
        
        # Calculate total result count
        result_count = sum(len(results[entity_type]) for entity_type in results)
        
        # Log search activity for analytics
        log_search_activity(
            query=query,
            entity_types=entity_types if entity_types else list(results.keys()),
            result_count=result_count,
            year=year
        )
    
    return render_template(
        'search/search.html',
        query=query,
        results=results,
        result_count=result_count,
        selected_types=entity_types,
        year=year,
        # Years for dropdown (last 10 years)
        years=list(range(datetime.now().year, datetime.now().year - 10, -1))
    )

@search_bp.route('/api/search', methods=['GET'])
@login_required
def api_search():
    """
    API endpoint for general intelligent search across entities.
    
    Query Parameters:
        q: The search query text
        types: Comma-separated list of entity types to search
        year: Year filter for entities with year attribute
        limit: Maximum number of results to return per entity type
        min_score: Minimum score (0-100) for fuzzy matching results
    
    Returns:
        JSON response with search results
    """
    query = request.args.get('q', '')
    entity_types_param = request.args.get('types', '')
    year_param = request.args.get('year')
    limit_param = request.args.get('limit', '5')
    min_score_param = request.args.get('min_score', '60')
    
    # Parse parameters
    entity_types = [t.strip() for t in entity_types_param.split(',')] if entity_types_param else None
    
    # Parse numeric parameters with defaults
    try:
        year = int(year_param) if year_param else None
        limit = int(limit_param)
        min_score = int(min_score_param)
    except ValueError:
        year = None
        limit = 5
        min_score = 60
    
    # Cap limit to prevent excessive queries
    limit = min(limit, 20)
    
    # Execute search
    results = {}
    result_count = 0
    
    if query:
        results = search_entities(
            query=query,
            entity_types=entity_types,
            year=year,
            limit=limit,
            min_score=min_score
        )
        
        result_count = sum(len(results[entity_type]) for entity_type in results)
        
        # Log search activity
        log_search_activity(
            query=query,
            entity_types=entity_types if entity_types else list(results.keys()),
            result_count=result_count,
            year=year
        )
    
    # Return JSON response
    return jsonify({
        'query': query,
        'results': results,
        'result_count': result_count,
        'entity_types': entity_types,
        'year': year
    })

@search_bp.route('/api/autocomplete', methods=['GET'])
@login_required
def api_autocomplete():
    """
    API endpoint for autocomplete suggestions.
    
    Query Parameters:
        q: The prefix text to autocomplete
        type: Entity type to search for autocomplete
        field: Specific field to match (optional)
        year: Year filter for entities with year attribute
        limit: Maximum number of suggestions to return
    
    Returns:
        JSON response with autocomplete suggestions
    """
    prefix = request.args.get('q', '')
    entity_type = request.args.get('type')
    field = request.args.get('field')
    year_param = request.args.get('year')
    limit_param = request.args.get('limit', '10')
    
    # Parse parameters with defaults
    try:
        year = int(year_param) if year_param else None
        limit = int(limit_param)
    except ValueError:
        year = None
        limit = 10
    
    # Cap limit to prevent excessive queries
    limit = min(limit, 20)
    
    # Get autocomplete suggestions
    suggestions = []
    
    if prefix and entity_type:
        suggestions = get_autocomplete_suggestions(
            prefix=prefix,
            entity_type=entity_type,
            field=field,
            year=year,
            limit=limit
        )
    
    # Return JSON response
    return jsonify({
        'query': prefix,
        'suggestions': suggestions,
        'count': len(suggestions)
    })

def init_search_routes(app):
    """
    Initialize search routes and register the blueprint with the Flask app.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(search_bp)
    
    # Create templates directory if it doesn't exist
    import os
    search_template_dir = os.path.join(app.template_folder, 'search')
    if not os.path.exists(search_template_dir):
        os.makedirs(search_template_dir)
    
    logger.info("Search routes initialized")