"""
Search routes for the Levy Calculation System.

This module provides route handlers for the intelligent search functionality
with fuzzy matching and autocomplete capabilities.
"""

import logging
from typing import Dict, List, Any, Optional

from flask import Blueprint, request, jsonify, render_template, current_app, g
from flask_login import login_required, current_user
from fuzzywuzzy import fuzz, process
from sqlalchemy import or_, and_, func

from app import db
from models import (
    User, TaxDistrict, TaxCode, Property, TaxCodeHistoricalRate, 
    LevyRate, LevyScenario, Forecast
)
from utils.search_utils import search_entities, autocomplete

logger = logging.getLogger(__name__)

# Create search blueprint
search_bp = Blueprint('search', __name__)


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
    query_text = request.args.get('q', '')
    entity_types = request.args.get('types', None)
    year = request.args.get('year', None)
    limit = request.args.get('limit', 10, type=int)
    min_score = request.args.get('min_score', 60, type=int)
    
    # Parse entity types if provided
    if entity_types:
        entity_types = entity_types.split(',')
    
    # Convert year to int if provided
    if year:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None
    
    # Perform search
    results = search_entities(
        query_text=query_text,
        entity_types=entity_types,
        year=year,
        limit=limit,
        min_score=min_score
    )
    
    # For API responses, include metadata
    response = {
        'query': query_text,
        'count': len(results),
        'results': results
    }
    
    return jsonify(response)


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
    query_prefix = request.args.get('q', '')
    entity_type = request.args.get('type', 'tax_district')
    field = request.args.get('field', None)
    year = request.args.get('year', None)
    limit = request.args.get('limit', 10, type=int)
    
    # Convert year to int if provided
    if year:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None
    
    # Get autocomplete suggestions
    suggestions = autocomplete(
        query_prefix=query_prefix,
        entity_type=entity_type,
        field=field,
        year=year,
        limit=limit
    )
    
    return jsonify(suggestions)


@search_bp.route('/search', methods=['GET'])
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
    query_text = request.args.get('q', '')
    entity_types = request.args.get('types', None)
    year = request.args.get('year', None)
    
    # Parse entity types if provided
    if entity_types:
        entity_types = entity_types.split(',')
    
    # Convert year to int if provided
    if year:
        try:
            year = int(year)
        except (ValueError, TypeError):
            year = None
    
    # Initial results for page load with query parameters
    results = []
    if query_text:
        results = search_entities(
            query_text=query_text,
            entity_types=entity_types,
            year=year,
            limit=10,
            min_score=60
        )
    
    # Get available years for filtering
    available_years = []
    try:
        # Query distinct years from TaxDistrict
        year_query = db.session.query(TaxDistrict.year).distinct().order_by(TaxDistrict.year.desc())
        available_years = [year[0] for year in year_query.all()]
    except Exception as e:
        logger.error(f"Error fetching available years: {str(e)}")
    
    return render_template(
        'search/search.html',
        query=query_text,
        results=results,
        selected_types=entity_types,
        selected_year=year,
        available_years=available_years
    )


def init_search_routes(app):
    """
    Initialize search routes and register the blueprint with the Flask app.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(search_bp)
    logger.info("Search routes initialized")