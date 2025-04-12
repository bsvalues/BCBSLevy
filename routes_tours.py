"""
Routes for guided tours in the Levy Calculation System.

This module provides endpoints for guided tours that help users
learn about different features of the application. Tours are
structured as interactive walkthroughs that highlight UI elements
and provide context for their functionality.
"""

from flask import Blueprint, jsonify, render_template, request, session

# Blueprint configuration
tours_bp = Blueprint('tours', __name__, url_prefix='/tours')

def register_routes(app):
    """
    Register the tours blueprint with the Flask application.
    
    Args:
        app: The Flask application instance
    """
    app.register_blueprint(tours_bp)
    app.logger.info('Tours blueprint registered')

@tours_bp.route('/')
def tours_home():
    """
    Render the tours homepage showing available guided tours.
    
    Returns:
        Rendered template for the tours homepage
    """
    tours = [
        {
            'id': 'welcome',
            'name': 'Welcome Tour',
            'description': 'Get oriented with the LevyMaster system and navigation.',
            'duration': '3-5 minutes',
            'icon': 'bi-info-circle'
        },
        {
            'id': 'dashboard',
            'name': 'Dashboard Tour',
            'description': 'Learn about the key metrics and features on your dashboard.',
            'duration': '2-3 minutes',
            'icon': 'bi-speedometer2'
        },
        {
            'id': 'calculator',
            'name': 'Levy Calculator Tour',
            'description': 'Learn how to calculate property tax levies effectively.',
            'duration': '4-6 minutes',
            'icon': 'bi-calculator'
        },
        {
            'id': 'data_import',
            'name': 'Data Import Tour',
            'description': 'Understand how to import and manage your data.',
            'duration': '3-4 minutes',
            'icon': 'bi-cloud-upload'
        },
        {
            'id': 'analysis',
            'name': 'Analytics Tools Tour',
            'description': 'Explore the various analytics and reporting tools.',
            'duration': '5-7 minutes',
            'icon': 'bi-graph-up'
        },
        {
            'id': 'mcp_army',
            'name': 'MCP Army Tour',
            'description': 'Get acquainted with the AI agent system.',
            'duration': '4-5 minutes',
            'icon': 'bi-robot'
        }
    ]
    
    return render_template('tours/index.html', tours=tours)

@tours_bp.route('/start/<tour_id>')
def start_tour(tour_id):
    """
    Start a guided tour by tour ID.
    
    Args:
        tour_id: The ID of the tour to start
        
    Returns:
        JSON response with tour configuration
    """
    # Store in session that this tour has been started
    tours_started = session.get('tours_started', [])
    if tour_id not in tours_started:
        tours_started.append(tour_id)
        session['tours_started'] = tours_started
    
    # Redirect to appropriate page based on tour type
    if tour_id == 'welcome':
        return jsonify({
            'redirect': '/',
            'start_tour': 'welcomeTour',
            'message': 'Welcome to the guided tour of LevyMaster!'
        })
    elif tour_id == 'dashboard':
        return jsonify({
            'redirect': '/dashboard',
            'start_tour': 'dashboardTour',
            'message': 'Welcome to the Dashboard tour!'
        })
    elif tour_id == 'calculator':
        return jsonify({
            'redirect': '/levy-calculator',
            'start_tour': 'calculatorTour',
            'message': 'Welcome to the Levy Calculator tour!'
        })
    elif tour_id == 'data_import':
        return jsonify({
            'redirect': '/data/import',
            'start_tour': 'dataImportTour',
            'message': 'Welcome to the Data Import tour!'
        })
    elif tour_id == 'analysis':
        return jsonify({
            'redirect': '/analysis/forecasting',
            'start_tour': 'analysisTour',
            'message': 'Welcome to the Analytics Tools tour!'
        })
    elif tour_id == 'mcp_army':
        return jsonify({
            'redirect': '/mcp-army-dashboard',
            'start_tour': 'mcpArmyTour',
            'message': 'Welcome to the MCP Army tour!'
        })
    else:
        return jsonify({
            'error': 'Tour not found',
            'redirect': '/tours'
        }), 404

@tours_bp.route('/progress')
def tour_progress():
    """
    Get the user's tour progress.
    
    Returns:
        JSON response with tour completion status
    """
    # Get progress from session
    tours_started = session.get('tours_started', [])
    tours_completed = session.get('tours_completed', [])
    
    all_tours = ['welcome', 'dashboard', 'calculator', 'data_import', 'analysis', 'mcp_army']
    progress = {
        'started': tours_started,
        'completed': tours_completed,
        'total': len(all_tours),
        'completed_count': len(tours_completed),
        'percentage': round((len(tours_completed) / len(all_tours)) * 100) if all_tours else 0
    }
    
    return jsonify(progress)

@tours_bp.route('/complete/<tour_id>', methods=['POST'])
def complete_tour(tour_id):
    """
    Mark a tour as completed.
    
    Args:
        tour_id: The ID of the tour to mark as completed
        
    Returns:
        JSON response confirming completion
    """
    # Store in session that this tour has been completed
    tours_completed = session.get('tours_completed', [])
    if tour_id not in tours_completed:
        tours_completed.append(tour_id)
        session['tours_completed'] = tours_completed
    
    return jsonify({
        'success': True,
        'message': f'Tour {tour_id} marked as completed',
        'completed': tours_completed
    })

@tours_bp.route('/reset', methods=['POST'])
def reset_tours():
    """
    Reset all tour progress.
    
    Returns:
        JSON response confirming reset
    """
    session.pop('tours_started', None)
    session.pop('tours_completed', None)
    
    return jsonify({
        'success': True,
        'message': 'All tour progress has been reset'
    })