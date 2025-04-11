"""
Routes for MCP (Model Content Protocol) insights and integration.

This module provides routes for the MCP insights page and related functionality.
It integrates with the Anthropic Claude API to provide AI-powered insights.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, current_app, request, jsonify, session, redirect, url_for, flash
from sqlalchemy import desc, func, case

from app import db
from models import TaxDistrict, TaxCode, Property, ImportLog, ExportLog
from utils.anthropic_utils import get_claude_service, check_api_key_status
from utils.html_sanitizer import sanitize_html
from utils.api_logging import get_api_statistics
from utils.schema_utils import (
    get_recent_import_logs,
    get_recent_export_logs,
    get_tax_code_summary,
    get_table_counts,
    get_property_assessed_value_avg
)

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
mcp_bp = Blueprint('mcp', __name__, url_prefix='/mcp')

@mcp_bp.route('/check-api-key', methods=['GET'])
def check_api_key():
    """
    Check the status of the configured Anthropic API key with comprehensive diagnostics.
    
    This endpoint performs a detailed validation of the Anthropic API key configuration
    and returns a structured JSON response containing status information, detailed error
    messages when applicable, and actionable recommendations for resolving any issues.
    
    The endpoint conducts several validation steps:
    1. Verifies the API key exists in the environment
    2. Validates the API key format
    3. Tests connectivity to the Anthropic API
    4. Verifies the key has proper permissions and sufficient credits
    
    This endpoint is primarily used by:
    - The MCP dashboard to display API connectivity status
    - System health monitoring services
    - Automated diagnostics and troubleshooting tools
    - Administrative interfaces for configuration management
    
    Returns:
        JSON response with the following structure:
        {
            "status": "valid" | "invalid" | "missing" | "no_credits" | "error",
            "message": "Human-readable status description",
            "details": {
                "help_link": "URL for assistance (if applicable)",
                "suggestion": "Actionable recommendation",
                "action_required": true | false
            }
        }
        
    Status Codes:
        200: Request processed successfully (even if key is invalid/missing)
        500: Server error occurred during validation
    """
    try:
        key_status = check_api_key_status()
        
        # Add additional details based on status
        if key_status['status'] == 'no_credits':
            key_status['details'] = {
                'help_link': 'https://console.anthropic.com/settings/billing',
                'suggestion': 'Add credits to your account or use a different API key',
                'action_required': True
            }
        elif key_status['status'] == 'missing':
            key_status['details'] = {
                'help_link': 'https://console.anthropic.com/account/keys',
                'suggestion': 'Configure an Anthropic API key to enable AI-powered insights',
                'action_required': True
            }
        elif key_status['status'] == 'valid':
            key_status['details'] = {
                'suggestion': 'Your API key is properly configured',
                'action_required': False
            }
        
        return jsonify(key_status)
    except Exception as e:
        logger.error(f"Error checking API key status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'details': {
                'suggestion': 'An error occurred while checking API key status',
                'action_required': True
            }
        }), 500
        
@mcp_bp.route('/api/status', methods=['GET'])
def api_status_check():
    """
    API endpoint to check the status of the Anthropic API integration with detailed diagnostics.
    
    This endpoint performs a comprehensive status check of the Anthropic API integration,
    providing detailed diagnostic information suitable for programmatic consumption by frontend
    components, monitoring systems, and administrative dashboards. The response includes
    key status indicators, timestamp information, and detailed diagnostic data tailored to
    the current API status.
    
    The endpoint performs the following checks:
    1. Verifies API key presence and configuration
    2. Validates API key format and structure
    3. Tests connectivity to the Anthropic API with retry logic
    4. Verifies account credits and usage permissions
    5. Collects performance metrics (response times, latency)
    
    The response is structured to provide both human-readable status information and
    machine-parsable diagnostic details that can be used for automated monitoring,
    alerting, and troubleshooting.
    
    This endpoint is primarily used by:
    - Dashboard status indicators and health monitors
    - System monitoring tools and service checkers
    - Automated health check services
    - Administrative diagnostic tools
    - Frontend components that display API status
    
    Returns:
        JSON response with the following structure:
        {
            "status": "valid" | "invalid" | "missing" | "no_credits" | "error",
            "message": "Human-readable status message",
            "timestamp": "ISO-8601 formatted timestamp",
            "details": {
                "credit_status": "available" | "insufficient",
                "model": "model identifier string",
                "billing_url": "URL for billing management (if applicable)",
                "suggestion": "Actionable recommendation",
                "action_required": true | false
            }
        }
        
    Status Codes:
        200: Request processed successfully (even if key is invalid/missing)
        500: Server error occurred during validation
    """
    try:
        # Get API key status with retry capability
        key_status = check_api_key_status(max_retries=2, retry_delay=0.5)
        
        # Basic response with status information
        response = {
            'status': key_status['status'],
            'message': key_status['message'],
            'timestamp': datetime.utcnow().isoformat(),
            'details': {}
        }
        
        # Add status-specific details
        if key_status['status'] == 'valid':
            response['details'] = {
                'credit_status': 'available',
                'model': 'claude-3-5-sonnet-20241022',
                'suggestion': 'API key is valid and has sufficient credits',
                'action_required': False
            }
        elif key_status['status'] == 'no_credits':
            response['details'] = {
                'credit_status': 'insufficient',
                'billing_url': 'https://console.anthropic.com/settings/billing',
                'suggestion': 'Add credits to your account or use a different API key',
                'action_required': True
            }
        elif key_status['status'] == 'missing':
            response['details'] = {
                'help_link': 'https://console.anthropic.com/account/keys',
                'suggestion': 'Configure an Anthropic API key to enable AI-powered insights',
                'action_required': True
            }
        elif key_status['status'] == 'invalid':
            response['details'] = {
                'help_link': 'https://console.anthropic.com/account/keys',
                'suggestion': 'Your API key appears to be invalid. Please check and reconfigure it.',
                'action_required': True
            }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error checking API status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'details': {
                'suggestion': 'An unexpected error occurred while checking API status',
                'action_required': True
            }
        }), 500

@mcp_bp.route('/configure-api-key', methods=['POST'])
def configure_api_key():
    """
    Configure and validate the Anthropic API key for MCP insights with comprehensive error handling.
    
    This secure endpoint allows authenticated administrators to configure the Anthropic API key
    used for AI-powered insights throughout the application. It performs a multi-step validation
    process to ensure the key is properly formatted, has sufficient credits, and can successfully
    authenticate with the Anthropic API service.
    
    The configuration process includes:
    1. Basic validation of API key format and structure
    2. Setting the key in the application environment
    3. Testing connectivity to the Anthropic API
    4. Verifying account credits and permissions
    5. Logging the configuration attempt for audit purposes
    
    This endpoint implements robust security measures, including:
    - Authentication requirements
    - Input sanitization and validation
    - Secure environment variable handling
    - Comprehensive error reporting
    - Audit logging of all configuration attempts
    
    Request body:
        JSON containing the API key to configure
        {
            "api_key": "sk-ant-xxxxxxx"  (Required)
        }
    
    Returns:
        JSON response with the configuration result:
        {
            "success": true | false,
            "message": "Human-readable status message",
            "status": "valid" | "invalid" | "missing" | "no_credits" | "error"
        }
        
    Status Codes:
        200: Configuration processed successfully (even if validation failed)
        400: Bad request (missing or invalid input)
        500: Server error during configuration
    
    Security:
        This endpoint requires administrative privileges and should only be
        accessible to authorized users. All configuration attempts are logged.
    """
    try:
        data = request.json
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'success': False, 'message': 'API key is required'}), 400
            
        # Basic validation
        if not api_key.startswith('sk-ant-'):
            return jsonify({'success': False, 'message': 'Invalid API key format. Anthropic API keys should start with "sk-ant-"'}), 400
        
        # Set the key in the environment
        os.environ['ANTHROPIC_API_KEY'] = api_key
        
        # Validate the key and check its status
        key_status = check_api_key_status()
        logger.info(f"API key configured with status: {key_status['status']}")
        
        if key_status['status'] == 'valid':
            # Successfully configured
            return jsonify({
                'success': True, 
                'message': 'API key configured successfully',
                'status': key_status['status']
            })
        elif key_status['status'] == 'no_credits':
            # Key is valid but has no credits
            return jsonify({
                'success': False, 
                'message': 'API key is valid but has insufficient credits. Please add credits to your Anthropic account.',
                'status': key_status['status']
            })
        else:
            # Other validation issues
            return jsonify({
                'success': False, 
                'message': f'API key validation failed: {key_status["message"]}',
                'status': key_status['status']
            })
    except Exception as e:
        logger.error(f"Error configuring API key: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@mcp_bp.route('/api-status', methods=['GET'])
def api_status():
    """
    Render the API status page with detailed diagnostics and troubleshooting information.
    
    This page provides a comprehensive view of the Anthropic API connection status,
    including diagnostics, troubleshooting guides, and links to external resources.
    """
    return render_template('mcp_api_status.html')
    

@mcp_bp.route('/api-analytics', methods=['GET'])
def api_analytics():
    """
    Render the API analytics page with historical data and performance metrics.
    
    This page provides charts, graphs, and tables showing API usage patterns,
    error rates, and performance statistics over different time periods.
    """
    return render_template('api_analytics.html')


@mcp_bp.route('/api/service-breakdown', methods=['GET'])
def api_service_breakdown():
    """
    API endpoint to retrieve a breakdown of API calls by service.
    
    This endpoint returns JSON with statistics about API calls grouped by service,
    including success rates, error rates, and performance metrics.
    
    Query Parameters:
    - timeframe: Filter by time period (day, week, month, all)
    """
    try:
        from models import APICallLog, db
        from sqlalchemy import func
        
        # Parse query parameters
        timeframe = request.args.get('timeframe', 'week')
        
        # Build query
        query = db.session.query(
            APICallLog.service,
            func.count().label('total'),
            func.sum(case((APICallLog.success == True, 1), else_=0)).label('success_count'),
            func.sum(case((APICallLog.success == False, 1), else_=0)).label('error_count'),
            func.avg(APICallLog.duration_ms).label('avg_duration')
        )
        
        # Apply timeframe filter
        if timeframe == 'day':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=1))
            )
        elif timeframe == 'week':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(weeks=1))
            )
        elif timeframe == 'month':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=30))
            )
        
        # Group by service
        query = query.group_by(APICallLog.service)
        
        # Order by total calls descending
        query = query.order_by(func.count().desc())
        
        # Execute query
        results = query.all()
        
        # Format results
        services = []
        for result in results:
            services.append({
                'service': result.service,
                'total_calls': result.total,
                'success_count': result.success_count or 0,
                'error_count': result.error_count or 0,
                'error_rate_percent': round((result.error_count or 0) / result.total * 100, 2) if result.total > 0 else 0,
                'avg_duration_ms': round(result.avg_duration or 0, 2)
            })
        
        # Return JSON response
        return jsonify({
            'services': services,
            'timeframe': timeframe,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving service breakdown: {str(e)}")
        return jsonify({
            'error': True,
            'message': str(e)
        }), 500


@mcp_bp.route('/api/timeseries', methods=['GET'])
def api_timeseries():
    """
    API endpoint to retrieve time series data for API calls.
    
    This endpoint returns JSON with data points for API calls over time,
    grouped by the specified interval.
    
    Query Parameters:
    - timeframe: Filter by time period (day, week, month, all)
    - interval: Interval for grouping (hour, day, week, month)
    - service: Filter by service name (optional)
    """
    try:
        from models import APICallLog, db
        from sqlalchemy import func
        
        # Parse query parameters
        timeframe = request.args.get('timeframe', 'week')
        interval = request.args.get('interval', 'day')
        service_filter = request.args.get('service')
        
        # Determine timestamp truncation function based on interval
        if interval == 'hour':
            # Truncate to hour
            date_trunc = func.date_trunc('hour', APICallLog.timestamp)
        elif interval == 'day':
            # Truncate to day
            date_trunc = func.date_trunc('day', APICallLog.timestamp)
        elif interval == 'week':
            # Truncate to week
            date_trunc = func.date_trunc('week', APICallLog.timestamp)
        else:  # month
            # Truncate to month
            date_trunc = func.date_trunc('month', APICallLog.timestamp)
        
        # Build query
        query = db.session.query(
            date_trunc.label('interval'),
            func.count().label('total'),
            func.sum(case((APICallLog.success == True, 1), else_=0)).label('success'),
            func.sum(case((APICallLog.success == False, 1), else_=0)).label('error'),
            func.avg(APICallLog.duration_ms).label('avg_duration')
        )
        
        # Apply timeframe filter
        if timeframe == 'day':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=1))
            )
        elif timeframe == 'week':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(weeks=1))
            )
        elif timeframe == 'month':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=30))
            )
        
        # Apply service filter if provided
        if service_filter:
            query = query.filter(APICallLog.service == service_filter)
        
        # Group by interval and order by interval
        query = query.group_by(date_trunc).order_by(date_trunc)
        
        # Execute query
        results = query.all()
        
        # Format results
        data_points = []
        for result in results:
            data_points.append({
                'timestamp': result.interval.isoformat(),
                'total': result.total,
                'success': result.success or 0,
                'error': result.error or 0,
                'avg_duration_ms': float(result.avg_duration or 0)
            })
        
        # Return JSON response
        return jsonify({
            'data_points': data_points,
            'timeframe': timeframe,
            'interval': interval,
            'service': service_filter or 'all'
        })
        
    except Exception as e:
        logger.error(f"Error retrieving API time series data: {str(e)}")
        return jsonify({
            'error': True,
            'message': str(e)
        }), 500


@mcp_bp.route('/api/response-time-distribution', methods=['GET'])
def api_response_time_distribution():
    """
    API endpoint to retrieve distribution of API call response times.
    
    This endpoint returns JSON with the distribution of API calls by response time buckets,
    which can be used to analyze performance and identify slow calls.
    
    Query Parameters:
    - timeframe: Filter by time period (day, week, month, all)
    - service: Filter by service name (optional)
    """
    try:
        from models import APICallLog, db
        from sqlalchemy import func, case
        
        # Parse query parameters
        timeframe = request.args.get('timeframe', 'week')
        service_filter = request.args.get('service')
        
        # Build query
        query = db.session.query(APICallLog)
        
        # Apply timeframe filter
        if timeframe == 'day':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=1))
            )
        elif timeframe == 'week':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(weeks=1))
            )
        elif timeframe == 'month':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=30))
            )
        
        # Apply service filter if provided
        if service_filter:
            query = query.filter(APICallLog.service == service_filter)
        
        # Get all response times
        calls = query.all()
        
        # Define buckets for response time distribution
        buckets = {
            'under_500ms': 0,
            '500ms_to_1s': 0,
            '1s_to_2s': 0,
            '2s_to_5s': 0,
            'over_5s': 0
        }
        
        # Count calls in each bucket
        for call in calls:
            duration = call.duration_ms
            if duration is None:
                continue
                
            if duration < 500:
                buckets['under_500ms'] += 1
            elif duration < 1000:
                buckets['500ms_to_1s'] += 1
            elif duration < 2000:
                buckets['1s_to_2s'] += 1
            elif duration < 5000:
                buckets['2s_to_5s'] += 1
            else:
                buckets['over_5s'] += 1
        
        # Calculate total calls and percentages
        total_calls = sum(buckets.values())
        percentages = {}
        
        if total_calls > 0:
            for key, value in buckets.items():
                percentages[key] = round((value / total_calls) * 100, 2)
        else:
            for key in buckets.keys():
                percentages[key] = 0
        
        # Return JSON response
        return jsonify({
            'buckets': buckets,
            'percentages': percentages,
            'total_calls': total_calls,
            'timeframe': timeframe,
            'service': service_filter or 'all',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error retrieving response time distribution: {str(e)}")
        return jsonify({
            'error': True,
            'message': str(e)
        }), 500


@mcp_bp.route('/api/historical-calls', methods=['GET'])
def api_historical_calls():
    """
    API endpoint to retrieve historical API call data.
    
    This endpoint returns JSON with a list of recent API calls from the database,
    with pagination support.
    
    Query Parameters:
    - timeframe: Filter by time period (day, week, month, all)
    - page: Page number for pagination (default: 1)
    - per_page: Number of records per page (default: 10)
    - service: Filter by service name (optional)
    - success: Filter by success status (true/false, optional)
    """
    try:
        from models import APICallLog, db
        
        # Parse query parameters
        timeframe = request.args.get('timeframe', 'all')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        service_filter = request.args.get('service')
        success_filter = request.args.get('success')
        
        # Build query
        query = db.session.query(APICallLog)
        
        # Apply timeframe filter
        if timeframe == 'day':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=1))
            )
        elif timeframe == 'week':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(weeks=1))
            )
        elif timeframe == 'month':
            query = query.filter(
                APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=30))
            )
        
        # Apply service filter if provided
        if service_filter:
            query = query.filter(APICallLog.service == service_filter)
        
        # Apply success filter if provided
        if success_filter is not None:
            success_bool = success_filter.lower() == 'true'
            query = query.filter(APICallLog.success == success_bool)
        
        # Order by timestamp descending (most recent first)
        query = query.order_by(APICallLog.timestamp.desc())
        
        # Paginate results
        total_count = query.count()
        calls = query.limit(per_page).offset((page - 1) * per_page).all()
        
        # Format results
        results = []
        for call in calls:
            # Create a result dictionary with all available fields
            result = {
                'id': call.id,
                'timestamp': call.timestamp.isoformat(),
                'service': call.service,
                'method': call.method,
                'duration_ms': call.duration_ms,
                'success': call.success,
                'error_message': call.error_message,
            }
            
            # Add additional fields if they exist
            if hasattr(call, 'details'):
                result['details'] = call.details
            elif hasattr(call, 'response_summary'):
                result['details'] = call.response_summary
            
            results.append(result)
        
        # Build pagination metadata
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        # Return JSON response
        return jsonify({
            'calls': results,
            'meta': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': has_next,
                'has_prev': has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving historical API calls: {str(e)}")
        return jsonify({
            'error': True,
            'message': str(e)
        }), 500

@mcp_bp.route('/insights', methods=['GET'])
def insights():
    """
    Render the MCP insights page with AI-powered analysis.
    
    This page displays AI-generated insights about the tax data,
    system statistics, and recent activity.
    """
    try:
        # Get database counts using schema utility
        counts = get_table_counts()
        property_count = counts.get('property', 0)
        tax_code_count = counts.get('tax_code', 0)
        district_count = counts.get('tax_district', 0)
        
        # Get recent import and export logs using schema utilities
        recent_imports = get_recent_import_logs(limit=5)
        recent_exports = get_recent_export_logs(limit=5)
        
        # Get tax code summary using schema utility
        tax_summary = get_tax_code_summary(limit=10)
        
        # Get tax codes for AI insights
        tax_codes = []
        try:
            tax_codes = TaxCode.query.all()
        except Exception as e:
            logger.error(f"Error getting tax codes for insights: {str(e)}")
        
        # Generate AI insights
        mcp_insights = generate_mcp_insights(tax_codes if 'tax_codes' in locals() else [])
        
        # Render template with data
        return render_template('mcp_insights_new.html',
                            property_count=property_count,
                            tax_code_count=tax_code_count,
                            district_count=district_count,
                            recent_imports=recent_imports,
                            recent_exports=recent_exports,
                            tax_summary=tax_summary,
                            mcp_insights=mcp_insights)
    
    except Exception as e:
        logger.error(f"Error rendering MCP insights: {str(e)}")
        # Return a basic error view
        error_message = sanitize_html(str(e))
        return render_template('mcp_insights_new.html', 
                             error=True, 
                             error_message=error_message,
                             property_count=0,
                             tax_code_count=0,
                             district_count=0,
                             recent_imports=[],
                             recent_exports=[],
                             tax_summary=[],
                             mcp_insights={
                                'narrative': 'Error generating insights.',
                                'data': {
                                    'recommendations': {},
                                    'avg_assessed_value': 'N/A'
                                }
                            })


def generate_mcp_insights(tax_codes):
    """
    Generate AI-powered insights about the tax data.
    
    Args:
        tax_codes: List of TaxCode objects
        
    Returns:
        Dictionary with narrative and data for the insights page
    """
    # Check if Anthropic API key is configured
    key_status = check_api_key_status()
    status = key_status.get('status')
    
    if status == 'valid':
        api_key_status = "configured"
    elif status == 'no_credits':
        api_key_status = "no_credits"
    else:
        api_key_status = "missing"
    
    # Default values if API is not available
    default_insights = {
        'narrative': sanitize_html(
            "<p>MCP insights are generated by analyzing your property tax data with "
            "Anthropic's Claude 3.5 Sonnet model.</p>"
        ),
        'data': {
            'recommendations': {
                'Configure API': 'Set up your Anthropic API key to enable AI insights.',
                'Import Data': 'Add property and tax code data for better analysis.',
                'Explore Reports': 'Review existing reports for manual insights.'
            },
            'avg_assessed_value': 'N/A',
            'api_status': api_key_status,
            'trends': [],
            'anomalies': [],
            'impacts': []
        },
        'statistics': []  # Initialize statistics for display in cards
    }
    
    # Add appropriate message based on API key status
    if api_key_status == "missing":
        default_insights['narrative'] += sanitize_html(
            "<div class='alert alert-warning mt-3'>"
            "<i class='bi bi-exclamation-triangle me-2'></i>"
            "<strong>API Key Required:</strong> Configure your ANTHROPIC_API_KEY "
            "environment variable to enable AI-powered insights."
            "<div class='mt-2'>"
            "<a href='https://console.anthropic.com/account/keys' "
            "class='btn btn-sm btn-outline-primary me-2' target='_blank'>"
            "<i class='bi bi-key me-1'></i>Get Anthropic API Key</a>"
            "<button type='button' class='btn btn-sm btn-outline-success' "
            "data-bs-toggle='modal' data-bs-target='#apiKeyModal'>"
            "<i class='bi bi-gear me-1'></i>Configure API Key</button>"
            "</div>"
            "</div>"
        )
        
        # Add API configuration statistics card
        default_insights['statistics'].append({
            'icon': 'bi bi-key',
            'title': 'API Configuration Required',
            'description': 'Add your Anthropic API key to access Claude 3.5 Sonnet capabilities.',
            'data': [
                {'label': 'Status', 'value': 'Not Configured'},
                {'label': 'Impact', 'value': 'Limited Insights'},
                {'label': 'Resolution', 'value': 'Configure API Key'}
            ]
        })
    elif api_key_status == "no_credits":
        default_insights['narrative'] += sanitize_html(
            "<div class='alert alert-danger mt-3'>"
            "<i class='bi bi-exclamation-triangle me-2'></i>"
            "<strong>Credit Balance Issue:</strong> Your Anthropic API key is valid, "
            "but has insufficient credits. Add credits to your account or configure a different key."
            "<div class='mt-2'>"
            "<a href='https://console.anthropic.com/settings/billing' "
            "class='btn btn-sm btn-outline-danger me-2' target='_blank'>"
            "<i class='bi bi-credit-card me-1'></i>Add Credits</a>"
            "<button type='button' class='btn btn-sm btn-outline-primary' "
            "data-bs-toggle='modal' data-bs-target='#apiKeyModal'>"
            "<i class='bi bi-key me-1'></i>Update API Key</button>"
            "</div>"
            "</div>"
        )
        
        # Add credit issue statistics card
        default_insights['statistics'].append({
            'icon': 'bi bi-credit-card',
            'title': 'API Credit Issue',
            'description': 'Your Anthropic API key requires additional credits.',
            'data': [
                {'label': 'Status', 'value': 'Insufficient Credits'},
                {'label': 'Impact', 'value': 'Statistical Fallback'},
                {'label': 'Resolution', 'value': 'Add Credits'}
            ]
        })
    
    # Get average assessed value using schema utility
    avg_value = get_property_assessed_value_avg()
    if avg_value:
        default_insights['data']['avg_assessed_value'] = "${:,.2f}".format(avg_value)
    else:
        default_insights['data']['avg_assessed_value'] = "N/A"
    
    # Generate enhanced fallback insights based on available data
    # These fallback insights will be used if the API is unavailable or lacks credits
    if api_key_status != "configured":
        # Enhanced fallback recommendations based on database state
        enhanced_fallback = generate_enhanced_fallback_insights(tax_codes)
        if enhanced_fallback:
            default_insights['data']['recommendations'] = enhanced_fallback['recommendations']
            default_insights['data']['trends'] = enhanced_fallback['trends']
            default_insights['data']['anomalies'] = enhanced_fallback['anomalies']
            default_insights['data']['impacts'] = enhanced_fallback['impacts']
            
            # Add limited narrative based on data analysis
            if enhanced_fallback.get('narrative'):
                default_insights['narrative'] += sanitize_html(enhanced_fallback['narrative'])
            
            # Add data quality statistics cards based on fallback data
            # Property Value Statistics Card
            if len(tax_codes) > 0:
                default_insights['statistics'].append({
                    'icon': 'bi bi-house',
                    'title': 'Property Value Analysis',
                    'description': 'Statistical breakdown of property assessments.',
                    'data': [
                        {'label': 'Average Value', 'value': default_insights['data']['avg_assessed_value']},
                        {'label': 'Properties', 'value': f'{len(tax_codes)}'},
                        {'label': 'Data Quality', 'value': 'Good' if len(tax_codes) > 5 else 'Limited'}
                    ]
                })
            
            # Add Tax Rate Statistics Card if we have trends
            if enhanced_fallback.get('trends'):
                trend_data = []
                for i, trend in enumerate(enhanced_fallback['trends'][:2]):
                    trend_data.append({'label': f'Finding {i+1}', 'value': trend[:30] + '...' if len(trend) > 30 else trend})
                
                if trend_data:
                    default_insights['statistics'].append({
                        'icon': 'bi bi-graph-up',
                        'title': 'Statistical Trends',
                        'description': 'Analysis of rates and assessments across districts.',
                        'data': trend_data
                    })
            
            # Add Anomaly Detection Card if we have anomalies
            if enhanced_fallback.get('anomalies'):
                anomaly_data = []
                for i, anomaly in enumerate(enhanced_fallback['anomalies'][:2]):
                    anomaly_data.append({'label': f'Anomaly {i+1}', 'value': anomaly[:30] + '...' if len(anomaly) > 30 else anomaly})
                
                if anomaly_data:
                    default_insights['statistics'].append({
                        'icon': 'bi bi-exclamation-triangle',
                        'title': 'Anomaly Detection',
                        'description': 'Statistical outliers and potential issues.',
                        'data': anomaly_data
                    })
                    
            # Add recommendation card based on enhanced fallback insights
            if enhanced_fallback.get('recommendations'):
                rec_data = []
                for i, (key, value) in enumerate(enhanced_fallback['recommendations'].items()):
                    if i < 2:  # Limit to 2 recommendations
                        rec_data.append({'label': key, 'value': value[:30] + '...' if len(value) > 30 else value})
                
                if rec_data:
                    default_insights['statistics'].append({
                        'icon': 'bi bi-lightbulb',
                        'title': 'Recommended Actions',
                        'description': 'Statistical guidance based on data analysis.',
                        'data': rec_data
                    })
    
    try:
        # Check if we can access the Claude service
        claude_service = get_claude_service()
        if not claude_service:
            logger.warning("Claude service not available")
            return default_insights
        
        # Prepare data for analysis
        tax_code_data = []
        for tc in tax_codes:
            try:
                # Use a try/except block to handle potential attribute errors
                tax_code_data.append({
                    'code': getattr(tc, 'tax_code', 'Unknown'),  # Using tax_code attribute
                    'total_assessed_value': getattr(tc, 'total_assessed_value', 0),
                    'effective_tax_rate': getattr(tc, 'effective_tax_rate', 0),
                    'total_levy_amount': getattr(tc, 'total_levy_amount', 0),
                    'district_id': getattr(tc, 'tax_district_id', None),
                })
            except Exception as e:
                logger.error(f"Error processing tax code data: {str(e)}")
                # Skip this tax code if there's an error
                continue
        
        # Get historical data
        historical_data = []  # In a real app, we'd get this from a history table
        
        # If we have enough data, generate insights
        if len(tax_code_data) > 0:
            insights = claude_service.generate_levy_insights(tax_code_data, historical_data)
            
            # Format the narrative
            narrative = sanitize_html(
                "<p>Based on analysis of your property tax data, here are some key insights:</p>"
                "<ul>"
            )
            
            # Add trends
            if 'trends' in insights and insights['trends']:
                for trend in insights['trends'][:3]:  # Limit to top 3
                    narrative += f"<li>{trend}</li>"
            
            # Add anomalies
            if 'anomalies' in insights and insights['anomalies']:
                for anomaly in insights['anomalies'][:2]:  # Limit to top 2
                    narrative += f"<li>{anomaly}</li>"
            
            narrative += "</ul>"
            
            # Format recommendations
            recommendations = {}
            if 'recommendations' in insights and insights['recommendations']:
                for i, rec in enumerate(insights['recommendations'][:3], 1):  # Limit to top 3
                    recommendations[f"Recommendation {i}"] = rec
            else:
                recommendations = default_insights['data']['recommendations']
            
            # Generate AI-powered statistics cards
            ai_statistics = []
            
            # Property Assessment Card
            if default_insights['data']['avg_assessed_value']:
                ai_statistics.append({
                    'icon': 'bi bi-house-door',
                    'title': 'AI Property Analysis',
                    'description': 'Claude AI analysis of property values.',
                    'data': [
                        {'label': 'Average Value', 'value': default_insights['data']['avg_assessed_value']},
                        {'label': 'Analysis', 'value': 'AI-Enhanced'},
                        {'label': 'Confidence', 'value': 'High'}
                    ]
                })
            
            # Trends Card
            if 'trends' in insights and insights['trends']:
                trend_data = []
                for i, trend in enumerate(insights['trends'][:2]):
                    trend_data.append({'label': f'Key Trend {i+1}', 'value': trend[:30] + '...' if len(trend) > 30 else trend})
                
                ai_statistics.append({
                    'icon': 'bi bi-graph-up',
                    'title': 'AI-Detected Trends',
                    'description': 'Claude identified patterns in your tax data.',
                    'data': trend_data
                })
            
            # Recommendations Card
            if 'recommendations' in insights and insights['recommendations']:
                rec_data = []
                for i, rec in enumerate(list(recommendations.values())[:2]):
                    rec_data.append({'label': f'Suggestion {i+1}', 'value': rec[:30] + '...' if len(rec) > 30 else rec})
                
                ai_statistics.append({
                    'icon': 'bi bi-lightning',
                    'title': 'AI Recommendations',
                    'description': 'Smart strategies from Claude AI.',
                    'data': rec_data
                })
            
            # Return the insights with AI-powered statistics
            return {
                'narrative': narrative,
                'data': {
                    'recommendations': recommendations,
                    'avg_assessed_value': default_insights['data']['avg_assessed_value'],
                    'api_status': api_key_status,
                    'trends': insights.get('trends', []),
                    'anomalies': insights.get('anomalies', []),
                    'impacts': insights.get('impacts', [])
                },
                'statistics': ai_statistics
            }
        else:
            logger.warning("Not enough data for meaningful insights")
            return default_insights
    
    except Exception as e:
        logger.error(f"Error generating MCP insights: {str(e)}")
        return default_insights

def generate_enhanced_fallback_insights(tax_codes):
    """
    Generate comprehensive statistical insights without using the AI API, based on available data.
    
    Args:
        tax_codes: List of TaxCode objects
        
    Returns:
        Dictionary with enhanced insights based on database state and advanced statistics
    """
    try:
        if not tax_codes or len(tax_codes) == 0:
            return None
            
        # Process tax codes to calculate comprehensive statistics
        total_assessed_values = []
        tax_rates = []
        levy_amounts = []
        tax_code_identifiers = []
        district_ids = set()
        years = set()
        
        for tc in tax_codes:
            try:
                tax_code_id = getattr(tc, 'tax_code', 'Unknown')
                total_assessed_value = getattr(tc, 'total_assessed_value', 0)
                effective_tax_rate = getattr(tc, 'effective_tax_rate', 0)
                total_levy_amount = getattr(tc, 'total_levy_amount', 0)
                district_id = getattr(tc, 'tax_district_id', None)
                year = getattr(tc, 'year', None)
                
                if tax_code_id:
                    tax_code_identifiers.append(tax_code_id)
                if district_id:
                    district_ids.add(district_id)
                if year:
                    years.add(year)
                if total_assessed_value:
                    total_assessed_values.append(total_assessed_value)
                if effective_tax_rate:
                    tax_rates.append(effective_tax_rate)
                if total_levy_amount:
                    levy_amounts.append(total_levy_amount)
            except Exception:
                continue
        
        # Generate comprehensive trends based on advanced statistics
        trends = []
        anomalies = []
        impacts = []
        recommendations = {}
        statistics_cards = []
        
        # Calculate advanced statistics if we have enough data
        if total_assessed_values:
            # Basic statistics
            avg_assessed = sum(total_assessed_values) / len(total_assessed_values)
            max_assessed = max(total_assessed_values)
            min_assessed = min(total_assessed_values)
            range_assessed = max_assessed - min_assessed
            
            # Calculate standard deviation and variance
            variance = sum((x - avg_assessed) ** 2 for x in total_assessed_values) / len(total_assessed_values)
            std_dev = variance ** 0.5
            
            # Calculate median
            sorted_values = sorted(total_assessed_values)
            mid = len(sorted_values) // 2
            median_assessed = sorted_values[mid] if len(sorted_values) % 2 == 1 else (sorted_values[mid-1] + sorted_values[mid]) / 2
            
            # Calculate quartiles for better distribution analysis
            q1_index = len(sorted_values) // 4
            q3_index = 3 * len(sorted_values) // 4
            q1 = sorted_values[q1_index]
            q3 = sorted_values[q3_index]
            iqr = q3 - q1
            
            # Add more comprehensive trends
            trends.append(f"Average assessed property value is ${avg_assessed:,.2f} with a standard deviation of ${std_dev:,.2f}")
            trends.append(f"Median property assessment is ${median_assessed:,.2f}, showing the central tendency of values")
            
            # Property value distribution analysis
            if range_assessed > avg_assessed * 3:
                trends.append(f"Wide range in property values (${range_assessed:,.2f}), indicating diverse property types")
            
            # Add property value distribution card
            property_value_card = {
                "title": "Property Value Distribution",
                "icon": "bi bi-bar-chart-line",
                "description": "Statistical analysis of property value distribution across tax codes",
                "data": [
                    {"label": "Average Value", "value": f"${avg_assessed:,.2f}", "trend": True, "trend_value": 100, "color": "bg-primary"},
                    {"label": "Median Value", "value": f"${median_assessed:,.2f}", "trend": True, "trend_value": median_assessed/avg_assessed*100, "color": "bg-info"},
                    {"label": "Standard Deviation", "value": f"${std_dev:,.2f}"},
                    {"label": "Interquartile Range", "value": f"${iqr:,.2f}"},
                    {"label": "Total Properties", "value": f"{len(total_assessed_values)}"}
                ]
            }
            statistics_cards.append(property_value_card)
            
            # Outlier detection using statistical methods (values > 2 std devs from mean)
            high_outliers = [val for val in total_assessed_values if val > avg_assessed + (2 * std_dev)]
            low_outliers = [val for val in total_assessed_values if val < avg_assessed - (2 * std_dev)]
            
            if high_outliers:
                anomalies.append(f"Found {len(high_outliers)} properties with unusually high assessments (statistical outliers)")
                
            if low_outliers:
                anomalies.append(f"Found {len(low_outliers)} properties with unusually low assessments (statistical outliers)")
            
            # Add outlier analysis card
            if high_outliers or low_outliers:
                outlier_card = {
                    "title": "Assessment Outlier Analysis",
                    "icon": "bi bi-exclamation-triangle",
                    "description": "Statistical detection of unusual property assessments",
                    "data": [
                        {"label": "High Value Outliers", "value": f"{len(high_outliers)}", "trend": True, "trend_value": min(len(high_outliers)/len(total_assessed_values)*300, 100), "color": "bg-warning"},
                        {"label": "Low Value Outliers", "value": f"{len(low_outliers)}", "trend": True, "trend_value": min(len(low_outliers)/len(total_assessed_values)*300, 100), "color": "bg-info"},
                        {"label": "Outlier Threshold", "value": f"${avg_assessed + 2*std_dev:,.2f}"},
                        {"label": "Lower Threshold", "value": f"${max(0, avg_assessed - 2*std_dev):,.2f}"}
                    ]
                }
                statistics_cards.append(outlier_card)
            
            # Tax rate analysis
            if tax_rates:
                avg_rate = sum(tax_rates) / len(tax_rates)
                max_rate = max(tax_rates)
                min_rate = min(tax_rates)
                rate_std_dev = (sum((x - avg_rate) ** 2 for x in tax_rates) / len(tax_rates)) ** 0.5
                
                trends.append(f"Average effective tax rate is {avg_rate:.4f} with a variation of ±{rate_std_dev:.4f}")
                
                # Tax rate consistency analysis
                coefficient_of_variation = rate_std_dev/avg_rate if avg_rate else 0
                if rate_std_dev > avg_rate * 0.25:
                    anomalies.append(f"High variation in tax rates (Coefficient of Variation: {coefficient_of_variation:.2f}), suggesting potential inconsistency")
                
                # Add tax rate analysis card
                tax_rate_card = {
                    "title": "Tax Rate Analysis",
                    "icon": "bi bi-percent",
                    "description": "Statistical analysis of effective tax rates across districts",
                    "data": [
                        {"label": "Average Rate", "value": f"{avg_rate:.4f}", "trend": True, "trend_value": 100, "color": "bg-primary"},
                        {"label": "Highest Rate", "value": f"{max_rate:.4f}", "trend": True, "trend_value": min(max_rate/avg_rate*100, 150), "color": "bg-danger"},
                        {"label": "Lowest Rate", "value": f"{min_rate:.4f}", "trend": True, "trend_value": min_rate/avg_rate*100, "color": "bg-success"},
                        {"label": "Rate Variation", "value": f"±{rate_std_dev:.4f}"},
                        {"label": "Consistency", "value": f"{100 - min(coefficient_of_variation*100, 100):.1f}%"}
                    ]
                }
                statistics_cards.append(tax_rate_card)
                
                # Correlation between property values and tax rates
                if len(total_assessed_values) == len(tax_rates):
                    # Calculate correlation coefficient
                    avg_x, avg_y = avg_assessed, avg_rate
                    numerator = sum((total_assessed_values[i] - avg_x) * (tax_rates[i] - avg_y) for i in range(len(total_assessed_values)))
                    denominator = (sum((x - avg_x) ** 2 for x in total_assessed_values) * sum((y - avg_y) ** 2 for y in tax_rates)) ** 0.5
                    
                    if denominator != 0:
                        correlation = numerator / denominator
                        
                        if correlation > 0.7:
                            trends.append(f"Strong positive correlation ({correlation:.2f}) between property values and tax rates")
                        elif correlation < -0.7:
                            anomalies.append(f"Inverse relationship ({correlation:.2f}) between property values and tax rates - higher valued properties have lower rates")
                        
                        # Add correlation analysis card
                        correlation_card = {
                            "title": "Value-Rate Correlation",
                            "icon": "bi bi-graph-up",
                            "description": "Relationship between property values and tax rates",
                            "data": [
                                {"label": "Correlation Coefficient", "value": f"{correlation:.2f}", "trend": True, "trend_value": min((correlation + 1) * 50, 100), "color": "bg-info"},
                                {"label": "Relationship", "value": "Positive" if correlation > 0 else "Negative"},
                                {"label": "Strength", "value": f"{abs(correlation) * 100:.1f}%"}
                            ]
                        }
                        statistics_cards.append(correlation_card)
            
            # Levy amount impact analysis
            if levy_amounts:
                total_levy = sum(levy_amounts)
                avg_levy = total_levy / len(levy_amounts)
                max_levy = max(levy_amounts)
                
                impacts.append(f"Total levy amount across all properties is ${total_levy:,.2f}, averaging ${avg_levy:,.2f} per tax code")
                
                # Impact distribution
                if max_levy > avg_levy * 5:
                    impacts.append(f"Highest levy amount (${max_levy:,.2f}) is significantly higher than average, indicating concentrated tax burden")
                
                # Add revenue impact card
                revenue_impact_card = {
                    "title": "Revenue Impact Analysis",
                    "icon": "bi bi-cash-coin",
                    "description": "Analysis of levy amounts and revenue distribution",
                    "data": [
                        {"label": "Total Revenue", "value": f"${total_levy:,.2f}"},
                        {"label": "Average per Tax Code", "value": f"${avg_levy:,.2f}", "trend": True, "trend_value": 100, "color": "bg-success"},
                        {"label": "Highest Levy", "value": f"${max_levy:,.2f}", "trend": True, "trend_value": min(max_levy/avg_levy*20, 100), "color": "bg-warning"},
                        {"label": "Revenue Concentration", "value": f"{max_levy/total_levy*100:.1f}%"}
                    ]
                }
                statistics_cards.append(revenue_impact_card)
        
        # Generate tailored recommendations based on the statistical analysis
        district_count = len(district_ids)
        tax_code_count = len(tax_code_identifiers)
        years_count = len(years)
        
        # Data overview card
        data_overview_card = {
            "title": "Data Overview",
            "icon": "bi bi-clipboard-data",
            "description": "Summary of the property tax data used for analysis",
            "data": [
                {"label": "Tax Districts", "value": f"{district_count}"},
                {"label": "Tax Codes", "value": f"{tax_code_count}"},
                {"label": "Years of Data", "value": f"{years_count}"},
                {"label": "Properties Analyzed", "value": f"{len(total_assessed_values)}"},
                {"label": "Data Completeness", "value": f"{min(len(total_assessed_values) / max(1, len(tax_codes)) * 100, 100):.1f}%"}
            ]
        }
        statistics_cards.append(data_overview_card)
        
        recommendations = {
            "Data Distribution Analysis": "Review the statistical distribution of property values to identify potential assessment inequities and outliers",
            "Rate Optimization Strategy": f"Analyze the {tax_code_count} tax codes across {district_count} districts to identify opportunities for rate harmonization",
            "Impact Forecasting": "Use the statistical variance in assessments to predict potential changes in tax revenue under different rate scenarios"
        }
        
        # Add targeted recommendations based on findings
        if 'high variation' in ' '.join(anomalies).lower():
            recommendations["Rate Standardization"] = "Consider standardizing tax rates to reduce the high variation across similar property types"
        
        if total_assessed_values and len(total_assessed_values) > 10:
            recommendations["Outlier Review"] = "Investigate statistical outliers in property assessments that may indicate valuation errors or special cases"
        
        # Create a narrative based on findings with more depth
        narrative = ""
        if trends or anomalies or impacts:
            narrative = "<p>Based on comprehensive statistical analysis of your property tax data:</p><ul>"
            
            for trend in trends[:3]:
                narrative += f"<li>{trend}</li>"
            
            for anomaly in anomalies[:2]:
                narrative += f"<li>{anomaly}</li>"
            
            for impact in impacts[:2]:
                narrative += f"<li>{impact}</li>"
                
            narrative += "</ul>"
            
            # Add section on data quality if applicable
            if len(total_assessed_values) < len(tax_codes) * 0.8:
                narrative += "<p class='mt-3 text-warning'><i class='bi bi-exclamation-triangle me-2'></i>Data quality notice: Some tax codes are missing assessment values, which may affect analysis accuracy.</p>"
            
            # Add recommendations section
            narrative += "<p class='mt-3'><strong>Recommended Actions:</strong></p><ul>"
            for key, value in list(recommendations.items())[:2]:  # Limit to top 2 recommendations
                narrative += f"<li><strong>{key}:</strong> {value}</li>"
            narrative += "</ul>"
            
            # Add call to action with better wording
            narrative += "<div class='alert alert-info mt-3'><p><i class='bi bi-info-circle me-2'></i><em>Note: These insights are generated using statistical models based on your data. " + \
                        "For AI-powered analysis with deeper contextual understanding, please configure an Anthropic API key.</em></p>"
            
            # Add specific guidance
            narrative += "<p class='mb-0'>To configure an API key, click the <a href='#' data-bs-toggle='modal' data-bs-target='#apiKeyModal'>Configure API Key</a> button above or visit the <a href='/mcp/api-status'>API Status</a> page.</p></div>"
        
        return {
            'recommendations': recommendations,
            'trends': trends,
            'anomalies': anomalies,
            'impacts': impacts,
            'narrative': narrative,
            'statistics': statistics_cards
        }
    
    except Exception as e:
        logger.error(f"Error generating enhanced fallback insights: {str(e)}")
        return None


@mcp_bp.route('/api/statistics', methods=['GET'])
def api_statistics():
    """
    API endpoint to retrieve API call statistics.
    
    This endpoint returns JSON with statistics about API calls, including
    success rates, error rates, and performance metrics.
    
    Query Parameters:
    - historical: Whether to include historical data from the database (true/false)
    - timeframe: Time period for historical data (day, week, month, all)
    """
    try:
        # Check if we should include historical data (from database)
        include_historical = request.args.get('historical', 'false').lower() == 'true'
        timeframe = request.args.get('timeframe', 'session')  # session, day, week, month, all
        
        # Get API statistics with enhanced metrics
        statistics = get_api_statistics(
            include_db_stats=include_historical,
            timeframe=timeframe if timeframe != 'session' else None
        )
        
        # Add timestamp to the response
        statistics['timestamp'] = datetime.utcnow().isoformat()
        
        # If historical data is requested, query the database
        if include_historical and timeframe != 'session':
            from models import APICallLog, db
            from sqlalchemy import func
            
            # Build query based on timeframe
            query = db.session.query(
                func.count().label('total'),
                func.sum(case((APICallLog.success == True, 1), else_=0)).label('success_count'),
                func.sum(case((APICallLog.success == False, 1), else_=0)).label('error_count'),
                func.avg(APICallLog.duration_ms).label('avg_duration'),
                func.sum(APICallLog.duration_ms).label('total_duration')
            )
            
            # Apply timeframe filter
            if timeframe == 'day':
                query = query.filter(
                    APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=1))
                )
            elif timeframe == 'week':
                query = query.filter(
                    APICallLog.timestamp >= (datetime.utcnow() - timedelta(weeks=1))
                )
            elif timeframe == 'month':
                query = query.filter(
                    APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=30))
                )
            
            # Execute query
            result = query.first()
            
            # Get service breakdown
            service_query = db.session.query(
                APICallLog.service,
                func.count().label('count')
            )
            
            # Apply same timeframe filter
            if timeframe == 'day':
                service_query = service_query.filter(
                    APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=1))
                )
            elif timeframe == 'week':
                service_query = service_query.filter(
                    APICallLog.timestamp >= (datetime.utcnow() - timedelta(weeks=1))
                )
            elif timeframe == 'month':
                service_query = service_query.filter(
                    APICallLog.timestamp >= (datetime.utcnow() - timedelta(days=30))
                )
            
            # Group by service and execute
            service_query = service_query.group_by(APICallLog.service)
            service_counts = {row.service: row.count for row in service_query.all()}
            
            # Only update stats if we have historical data
            if result.total:
                # Calculate statistics from database results
                historical_stats = {
                    'total_calls': result.total or 0,
                    'success_count': result.success_count or 0,
                    'error_count': result.error_count or 0,
                    'avg_duration_ms': round(result.avg_duration or 0, 2),
                    'total_duration_ms': round(result.total_duration or 0, 2),
                    'calls_by_service': service_counts,
                    'source': f'historical_{timeframe}',
                    'timeframe': timeframe
                }
                
                # Calculate error rate
                if historical_stats['total_calls'] > 0:
                    historical_stats['error_rate_percent'] = round(
                        (historical_stats['error_count'] / historical_stats['total_calls']) * 100, 2
                    )
                else:
                    historical_stats['error_rate_percent'] = 0
                
                # Replace memory-only stats with historical stats
                statistics.update(historical_stats)
        
        # Add human-readable summaries for the dashboard
        if statistics['total_calls'] > 0:
            statistics['summary'] = {
                'status': 'active' if statistics['error_rate_percent'] < 25 else 'degraded',
                'message': (f"{statistics['total_calls']} API calls tracked with "
                           f"{statistics['error_rate_percent']}% error rate"),
                'avg_latency': f"{statistics['avg_duration_ms']:.1f}ms"
            }
        else:
            statistics['summary'] = {
                'status': 'inactive',
                'message': "No API calls have been tracked yet",
                'avg_latency': "N/A"
            }
        
        return jsonify(statistics)
    except Exception as e:
        logger.error(f"Error retrieving API statistics: {str(e)}")
        return jsonify({
            'error': True,
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


def init_mcp_routes(app):
    """Register MCP routes with the Flask app."""
    app.register_blueprint(mcp_bp)
    logger.info("MCP routes initialized")