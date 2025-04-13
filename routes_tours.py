"""
Routes for guided tours management in the LevyMaster application.

This module provides routes for managing and tracking guided tours, including:
- Tour index page listing available tours
- Tour completion tracking
- Tour statistics and analytics
"""

import json
from datetime import datetime
import logging

# Flask imports - these are already installed in the environment
try:
    from flask import Blueprint, render_template, request, jsonify, session, current_app
except ImportError:
    pass  # Handle gracefully in development environment

# SQLAlchemy imports - these are already installed in the environment
try:
    from sqlalchemy import func
except ImportError:
    pass  # Handle gracefully in development environment

# Local imports
from models import db, User

# Initialize blueprint
tours_bp = Blueprint('tours', __name__, url_prefix='/tours')

# Setup logging
logger = logging.getLogger(__name__)

@tours_bp.route('/')
def tour_index():
    """
    Display the tour index page with all available tours.
    
    Returns:
        The rendered tours index template.
    """
    # Define available tours
    available_tours = [
        {
            'id': 'welcomeTour',
            'name': 'Welcome Tour',
            'description': 'Overview of the LevyMaster navigation and main features',
            'duration': '2-3 minutes',
            'icon': 'bi-info-circle'
        },
        {
            'id': 'dashboardTour',
            'name': 'Dashboard Tour',
            'description': 'Guide to understanding and utilizing the dashboard',
            'duration': '2 minutes',
            'icon': 'bi-speedometer2'
        },
        {
            'id': 'calculatorTour',
            'name': 'Levy Calculator Tour',
            'description': 'Step-by-step guide to using the levy calculator',
            'duration': '3-4 minutes',
            'icon': 'bi-calculator'
        },
        {
            'id': 'dataHubTour',
            'name': 'Data Hub Tour',
            'description': 'Overview of data import, export and management features',
            'duration': '3 minutes',
            'icon': 'bi-database'
        },
        {
            'id': 'mcpArmyTour',
            'name': 'AI & Agents Tour',
            'description': 'Guide to using AI-powered features and agents',
            'duration': '3 minutes',
            'icon': 'bi-robot'
        },
        {
            'id': 'reportsTour',
            'name': 'Reports Tour',
            'description': 'Guide to generating and customizing reports',
            'duration': '2-3 minutes',
            'icon': 'bi-file-earmark-text'
        }
    ]
    
    # Get tour completion statistics
    completion_stats = get_tour_completion_stats()
    
    # Add completion status to each tour (if authenticated)
    user_completed_tours = []
    if hasattr(session, 'user_id'):
        user_completed_tours = get_user_completed_tours(session.get('user_id'))
    
    for tour in available_tours:
        tour['completed'] = str(tour['id'] in user_completed_tours)
    
    return render_template(
        'tours/index.html',
        tours=available_tours,
        stats=completion_stats,
        page_title="Guided Tours"
    )

@tours_bp.route('/start/<tour_id>')
def start_tour(tour_id):
    """
    Start a specific tour by redirecting to the appropriate page.
    
    Args:
        tour_id: The ID of the tour to start
        
    Returns:
        A redirect to the appropriate starting page with tour parameter
    """
    # Map of tour starting points
    tour_starting_points = {
        'welcomeTour': '/?start_tour=welcomeTour',
        'dashboardTour': '/dashboard?start_tour=dashboardTour',
        'calculatorTour': '/levy-calculator?start_tour=calculatorTour',
        'dataHubTour': '/data/import?start_tour=dataHubTour',
        'mcpArmyTour': '/mcp-army-dashboard?start_tour=mcpArmyTour',
        'reportsTour': '/reports?start_tour=reportsTour'
    }
    
    # Log tour start
    logger.info(f"User {session.get('user_id', 'anonymous')} started tour: {tour_id}")
    
    # Return the redirect URL as JSON
    return jsonify({
        'redirect': tour_starting_points.get(tour_id, '/?start_tour=' + tour_id)
    })

@tours_bp.route('/complete/<tour_id>', methods=['POST'])
def complete_tour(tour_id):
    """
    Record a completed tour for the current user.
    
    Args:
        tour_id: The ID of the completed tour
        
    Returns:
        JSON response with success status
    """
    # Log tour completion
    logger.info(f"User {session.get('user_id', 'anonymous')} completed tour: {tour_id}")
    
    # If user is authenticated, store completion in session
    if hasattr(session, 'user_id'):
        # Get current completed tours
        completed_tours = session.get('completed_tours', [])
        
        # Add the current tour if not already completed
        if tour_id not in completed_tours:
            completed_tours.append(tour_id)
            session['completed_tours'] = completed_tours
            
            # Save to database if we have a user model with tour tracking
            try:
                record_tour_completion_in_db(session.get('user_id'), tour_id)
            except Exception as e:
                logger.error(f"Error recording tour completion: {str(e)}")
    
    return jsonify({'success': True})

def get_user_completed_tours(user_id):
    """
    Get list of tours completed by a specific user.
    
    Args:
        user_id: The user ID to check
        
    Returns:
        List of completed tour IDs
    """
    # First check session
    if hasattr(session, 'completed_tours'):
        return session.get('completed_tours', [])
    
    # Then check database if we have a UserTourCompletion model
    # This would require adding a model for tracking tour completions
    # For now, return empty list or session data
    return []

def record_tour_completion_in_db(user_id, tour_id):
    """
    Record a tour completion in the database.
    
    Args:
        user_id: The user ID
        tour_id: The tour ID
        
    Returns:
        None
    """
    # This would require adding a model for tracking tour completions
    # For now, just log the completion
    logger.info(f"Recording tour completion in database: User {user_id}, Tour {tour_id}")
    
    # If you add a UserTourCompletion model later, you could use:
    # completion = UserTourCompletion(user_id=user_id, tour_id=tour_id)
    # db.session.add(completion)
    # db.session.commit()

def get_tour_completion_stats():
    """
    Get statistics about tour completions.
    
    Returns:
        Dictionary with tour completion statistics
    """
    # This would require querying the database for real stats
    # For now, return placeholder stats
    return {
        'total_tours_completed': 0,
        'most_popular_tour': 'welcomeTour',
        'completion_rate': 0
    }

def register_tour_routes(app):
    """
    Register the tours blueprint with the Flask application.
    
    Args:
        app: The Flask application instance
        
    Returns:
        None
    """
    app.register_blueprint(tours_bp)
    logger.info('Tours routes registered')