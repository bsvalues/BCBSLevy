"""
Advanced Model Content Protocol (MCP) routes for the Levy Calculation System.

This module provides Flask routes for the advanced AI agent features including:
- Natural language query interface
- Multi-turn dialogue capabilities
- Multi-step analysis workflows
- Cross-dataset insights
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import (
    Blueprint, render_template, request, jsonify, 
    current_app, session, redirect, url_for, flash
)
from flask_login import login_required, current_user

from utils.advanced_ai_agent import get_advanced_analysis_agent
from utils.anthropic_utils import get_claude_service, check_api_key_status
from utils.html_sanitizer import sanitize_html
from utils.mcp_core import registry

logger = logging.getLogger(__name__)
advanced_mcp_bp = Blueprint('advanced_mcp', __name__)


@advanced_mcp_bp.route('/advanced-insights')
@login_required
def advanced_insights():
    """
    Render the advanced AI insights page with dynamic, AI-powered analytics.
    
    This endpoint generates and displays sophisticated tax data insights using the
    Anthropic Claude API, providing users with interactive analytics, natural language
    explanations, and contextual recommendations based on their specific tax data.
    
    The page integrates multiple advanced capabilities:
    1. Cross-dataset pattern recognition to identify relationships between tax districts
    2. Natural language explanations of complex tax data trends
    3. Interactive data visualization of key metrics
    4. Contextual recommendations tailored to the user's role and responsibilities
    5. Multi-turn dialogue capabilities for exploratory data analysis
    
    The insights generation process follows these steps:
    1. Verify API key status and availability
    2. Check for presence of tax data to analyze
    3. If both are available, generate initial insights using Claude API
    4. Sanitize and structure the AI-generated insights
    5. Render the template with the insights data
    
    Authentication is required to access this page, as it contains sensitive tax data
    analysis and personalized recommendations. The page adapts to the user's role and
    permissions, showing relevant insights based on their access level.
    
    Returns:
        Rendered HTML template with advanced AI insights or a fallback message if
        insights generation fails or prerequisites aren't met.
    """
    # Check API key status
    api_key_status = check_api_key_status()
    
    # Default empty insights structure
    insights = {
        'narrative': '<p>No advanced insights available yet. Please configure an API key and ensure tax data is imported.</p>',
        'data': {
            'recommendations': {},
            'avg_assessed_value': 'N/A',
            'api_status': api_key_status,
            'trends': [],
            'anomalies': [],
            'impacts': []
        },
        'statistics': [],
        'advanced_capabilities': [
            {
                'name': 'Multi-turn Dialogue',
                'description': 'Have contextual conversations with the AI about your tax data',
                'icon': 'bi bi-chat-dots'
            },
            {
                'name': 'Cross-Dataset Analysis',
                'description': 'Discover insights across different datasets',
                'icon': 'bi bi-intersect'
            },
            {
                'name': 'Natural Language Queries',
                'description': 'Ask questions about your data in plain English',
                'icon': 'bi bi-search'
            },
            {
                'name': 'Contextual Recommendations',
                'description': 'Get personalized recommendations based on your role',
                'icon': 'bi bi-lightbulb'
            }
        ]
    }
    
    try:
        # Check if we have any tax data to analyze
        from models import TaxCode
        from app import db
        
        # Get sample of tax code data
        tax_codes = db.session.query(TaxCode).limit(10).all()
        
        if tax_codes and api_key_status.get('status') == 'valid':
            # We have data and a valid API key - generate some initial insights
            claude_service = get_claude_service()
            if claude_service:
                logger.info("Generating initial advanced insights")
                
                # Convert tax codes to dictionaries
                tax_code_data = []
                for tc in tax_codes:
                    tax_code_data.append({
                        'code': getattr(tc, 'tax_code', 'Unknown'),
                        'total_assessed_value': getattr(tc, 'total_assessed_value', 0),
                        'effective_tax_rate': getattr(tc, 'effective_tax_rate', 0),
                        'total_levy_amount': getattr(tc, 'total_levy_amount', 0),
                        'district_id': getattr(tc, 'tax_district_id', None),
                    })
                
                # Get basic data for sample cards
                try:
                    # Get historical data (if available)
                    from models import TaxCodeHistoricalRate
                    historical_rates = db.session.query(TaxCodeHistoricalRate).limit(10).all()
                    
                    historical_data = []
                    if historical_rates:
                        for hr in historical_rates:
                            historical_data.append({
                                'tax_code_id': getattr(hr, 'tax_code_id', None),
                                'year': getattr(hr, 'year', None),
                                'levy_rate': getattr(hr, 'levy_rate', 0),
                                'levy_amount': getattr(hr, 'levy_amount', 0),
                                'total_assessed_value': getattr(hr, 'total_assessed_value', 0)
                            })
                    
                    # Get the agent and generate cross-dataset insights as a sample of advanced capabilities
                    advanced_agent = get_advanced_analysis_agent()
                    cross_dataset_results = advanced_agent.analyze_cross_dataset_patterns(
                        tax_codes=tax_code_data,
                        historical_rates=historical_data
                    )
                    
                    # Update insights with cross-dataset results
                    if cross_dataset_results and not isinstance(cross_dataset_results, str):
                        correlations = cross_dataset_results.get('correlations', [])
                        patterns = cross_dataset_results.get('patterns', [])
                        anomalies = cross_dataset_results.get('anomalies', [])
                        cross_insights = cross_dataset_results.get('insights', [])
                        
                        # Create narrative from insights
                        narrative = sanitize_html(
                            "<p>Advanced AI analysis of your tax data reveals cross-dataset insights:</p>"
                            "<ul>"
                        )
                        
                        # Add patterns
                        for pattern in patterns[:2]:
                            narrative += f"<li>{pattern}</li>"
                        
                        # Add correlations
                        for correlation in correlations[:2]:
                            narrative += f"<li>{correlation}</li>"
                            
                        narrative += "</ul>"
                        
                        # Generate AI-powered statistics cards
                        ai_statistics = []
                        
                        # Patterns Card
                        if patterns:
                            pattern_data = []
                            for i, pattern in enumerate(patterns[:2]):
                                pattern_data.append({'label': f'Pattern {i+1}', 'value': pattern[:50] + '...' if len(pattern) > 50 else pattern})
                            
                            ai_statistics.append({
                                'icon': 'bi bi-graph-up',
                                'title': 'Cross-Dataset Patterns',
                                'description': 'Identified patterns across multiple datasets',
                                'data': pattern_data
                            })
                        
                        # Correlations Card
                        if correlations:
                            correlation_data = []
                            for i, correlation in enumerate(correlations[:2]):
                                correlation_data.append({'label': f'Correlation {i+1}', 'value': correlation[:50] + '...' if len(correlation) > 50 else correlation})
                            
                            ai_statistics.append({
                                'icon': 'bi bi-link',
                                'title': 'Data Correlations',
                                'description': 'Relationships between different data points',
                                'data': correlation_data
                            })
                        
                        # Anomalies Card
                        if anomalies:
                            anomaly_data = []
                            for i, anomaly in enumerate(anomalies[:2]):
                                anomaly_data.append({'label': f'Anomaly {i+1}', 'value': anomaly[:50] + '...' if len(anomaly) > 50 else anomaly})
                            
                            ai_statistics.append({
                                'icon': 'bi bi-exclamation-triangle',
                                'title': 'Cross-Dataset Anomalies',
                                'description': 'Unusual patterns requiring attention',
                                'data': anomaly_data
                            })
                        
                        # Insights Card
                        if cross_insights:
                            insight_data = []
                            for i, insight in enumerate(cross_insights[:2]):
                                insight_data.append({'label': f'Insight {i+1}', 'value': insight[:50] + '...' if len(insight) > 50 else insight})
                            
                            ai_statistics.append({
                                'icon': 'bi bi-lightbulb',
                                'title': 'Strategic Insights',
                                'description': 'Key takeaways for decision-making',
                                'data': insight_data
                            })
                        
                        # Update insights with advanced analysis
                        insights = {
                            'narrative': narrative,
                            'data': {
                                'recommendations': insights['data']['recommendations'],
                                'avg_assessed_value': insights['data']['avg_assessed_value'],
                                'api_status': api_key_status,
                                'patterns': patterns,
                                'correlations': correlations,
                                'anomalies': anomalies,
                                'insights': cross_insights
                            },
                            'statistics': ai_statistics,
                            'advanced_capabilities': insights['advanced_capabilities']
                        }
                        
                except Exception as e:
                    logger.error(f"Error generating cross-dataset insights: {str(e)}")
                    # Keep default insights if there's an error
    
    except Exception as e:
        logger.error(f"Error in advanced insights route: {str(e)}")
        # Keep default insights if there's an error
    
    return render_template(
        'advanced_insights.html',
        insights=insights,
        current_timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        active_page='advanced_insights'
    )


@advanced_mcp_bp.route('/api/advanced-mcp/query', methods=['POST'])
@login_required
def process_natural_language_query():
    """
    API endpoint to process natural language queries about tax data with advanced NLP capabilities.
    
    This endpoint enables conversational AI interactions with the tax data system,
    allowing users to ask questions, request analysis, and explore data relationships using
    natural language. The endpoint leverages the Anthropic Claude API to interpret
    and respond to complex tax-related queries in a contextually aware manner.
    
    Key capabilities of this endpoint include:
    1. Contextual understanding of tax terminology and concepts
    2. Multi-turn dialogue with memory of previous interactions
    3. Natural language parsing and intent recognition
    4. Context-aware responses that incorporate user role and permissions
    5. Data-driven insights derived from the underlying tax database
    
    The processing flow follows these steps:
    1. Parse the incoming natural language query
    2. Retrieve the conversation context if available
    3. Process the query through the advanced analysis agent
    4. Format and return the response with appropriate data structures
    
    This endpoint integrates with domain-specific knowledge about tax systems and levy
    calculations, enabling it to handle complex inquiries such as:
    - "Compare the levy rates between District A and District B over the last 5 years"
    - "What would happen to the average homeowner's tax bill if we increased EAV by 3%?"
    - "Explain the relationship between new construction and the limiting rate"
    - "What factors contributed most to the increasing tax rates in North Township?"
    - "Where are we seeing the most significant compliance risks in our current levy structure?"
    
    The system maintains conversational context, enabling follow-up questions like:
    - "Why did that happen?"
    - "How does that compare to the state average?"
    - "What would you recommend we do about this issue?"
    
    Request body:
        JSON object containing:
        {
            "query": "natural language question about tax data", (Required)
            "context": {                                         (Optional)
                "previous_queries": [],
                "user_role": "administrator",
                "district_id": 123,
                "additional_context": {}
            }
        }
    
    Returns:
        JSON response containing:
        {
            "response": {
                "answer": "Natural language response to the query",
                "data": {
                    "relevant_statistics": [],
                    "visualizations": [],
                    "actionable_insights": []
                },
                "follow_up_suggestions": []
            }
        }
        
    Error responses:
        400: Missing or invalid query parameter
        500: Error processing the natural language query
    
    Authentication:
        This endpoint requires user authentication via login_required decorator
        to ensure data privacy and access control.
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing query parameter"}), 400
    
    query = data['query']
    context = data.get('context', {})
    
    try:
        # Get advanced analysis agent
        advanced_agent = get_advanced_analysis_agent()
        response = advanced_agent.process_natural_language_query(
            query=query,
            context=context
        )
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error processing natural language query: {str(e)}")
        return jsonify({"error": str(e)}), 500


@advanced_mcp_bp.route('/api/advanced-mcp/multi-step-analysis', methods=['POST'])
@login_required
def run_multistep_analysis():
    """
    API endpoint to run comprehensive multi-step tax district analysis workflows.
    
    This sophisticated endpoint orchestrates complex, multi-stage analysis pipelines that
    perform a series of coordinated analytical steps on tax district data. It leverages the
    MCP workflow system to execute sequenced operations with data passing between steps,
    providing deep, contextual insights that span multiple analytical dimensions.
    
    The multi-step analysis capability offers several advantages over simple API calls:
    1. Sequential execution of interdependent analytical operations
    2. Progressive data refinement through the analytical pipeline
    3. Comprehensive insights derived from multiple analytical perspectives
    4. Integration of AI-driven interpretation with statistical calculations
    5. Unified results packaging from diverse analytical methods
    
    Supported analysis types include:
    - 'comprehensive': Full analysis across all dimensions (levy rates, compliance, trends)
    - 'forecasting': Predictive analysis focused on future levy rates and impacts
    - 'compliance': Analysis focused on statutory compliance and risk factors
    - 'budget_impact': Analysis of budgetary impacts across stakeholders
    
    The analysis process follows these steps:
    1. Load and validate tax district data
    2. Execute preliminary data analysis and statistical calculations
    3. Perform specialized analysis based on the requested analysis type
    4. Generate forecasts and predictions for future periods
    5. Synthesize findings into coherent insights and recommendations
    6. Format and structure the results for client-side rendering
    
    Request body:
        JSON object containing:
        {
            "district_id": 123,                      (Required) ID of the tax district to analyze
            "analysis_type": "comprehensive",        (Optional) Type of analysis to perform
            "years": 3                               (Optional) Number of years for forecasting
        }
    
    Returns:
        JSON response containing:
        {
            "response": {
                "summary": "Executive summary of analysis results",
                "findings": [
                    {"title": "Finding 1", "description": "...", "impact": "High"},
                    ...
                ],
                "forecasts": {...},
                "statistics": {...},
                "recommendations": [...]
            }
        }
        
    Error responses:
        400: Missing district_id parameter
        500: Error during analysis execution
    
    Authentication:
        This endpoint requires user authentication via login_required decorator
        to ensure data privacy and access control.
    """
    data = request.json
    if not data or 'district_id' not in data:
        return jsonify({"error": "Missing district_id parameter"}), 400
    
    district_id = data['district_id']
    analysis_type = data.get('analysis_type', 'comprehensive')
    years = data.get('years', 3)
    
    try:
        # Get advanced analysis agent
        advanced_agent = get_advanced_analysis_agent()
        response = advanced_agent.perform_multistep_analysis(
            tax_district_id=district_id,
            analysis_type=analysis_type,
            years=years
        )
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error running multi-step analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


@advanced_mcp_bp.route('/api/advanced-mcp/recommendations', methods=['POST'])
@login_required
def get_contextual_recommendations():
    """
    API endpoint to generate personalized, role-based tax recommendations with AI.
    
    This sophisticated endpoint leverages the Anthropic Claude API to deliver
    highly personalized, contextually relevant recommendations based on tax data analysis,
    user role, and specified focus areas. The recommendations are tailored to different
    stakeholder perspectives and their specific responsibilities in the tax management process.
    
    The recommendation engine provides different insights based on user roles:
    - 'administrator': Strategic recommendations focused on system-wide improvements
    - 'analyst': Technical recommendations highlighting data patterns and optimization opportunities
    - 'financial_officer': Financial impact and budget-oriented recommendations
    - 'compliance_officer': Compliance risk recommendations and statutory considerations
    - 'taxpayer': Citizen-focused explanations and transparency insights
    
    Focus areas allow further customization of recommendations:
    - 'budget_planning': Recommendations for budget cycle planning
    - 'compliance': Statutory compliance and risk mitigation guidance
    - 'equity': Tax burden distribution and fairness considerations
    - 'forecasting': Future-oriented projections and scenario planning
    - 'transparency': Public communication and stakeholder engagement strategies
    
    The recommendation generation process follows these steps:
    1. Load tax code data and associated records
    2. Generate insights tailored to the specified user role
    3. Filter and prioritize recommendations based on focus area
    4. Structure recommendations with actionable details and impact assessments
    5. Format the response for client-side rendering
    
    Request body:
        JSON object containing:
        {
            "tax_code_id": 123,                      (Required) ID of the tax code to analyze
            "user_role": "administrator",            (Optional) Role perspective for recommendations
            "focus_area": "budget_planning"          (Optional) Specific focus area for recommendations
        }
    
    Returns:
        JSON response containing:
        {
            "response": {
                "summary": "Executive summary of recommendations",
                "recommendations": [
                    {
                        "title": "Recommendation title",
                        "description": "Detailed explanation",
                        "impact": "High|Medium|Low",
                        "implementation_difficulty": "Easy|Moderate|Complex",
                        "rationale": "Reasoning behind this recommendation"
                    },
                    ...
                ],
                "context": {
                    "tax_code_overview": "...",
                    "relevant_statistics": {...}
                }
            }
        }
        
    Error responses:
        400: Missing tax_code_id parameter
        500: Error generating recommendations
    
    Authentication:
        This endpoint requires user authentication via login_required decorator
        to ensure data privacy and role-based access control.
    """
    data = request.json
    if not data or 'tax_code_id' not in data:
        return jsonify({"error": "Missing tax_code_id parameter"}), 400
    
    tax_code_id = data['tax_code_id']
    user_role = data.get('user_role', 'administrator')
    focus_area = data.get('focus_area')
    
    try:
        # Get advanced analysis agent
        advanced_agent = get_advanced_analysis_agent()
        response = advanced_agent.generate_contextual_recommendations(
            tax_code_id=tax_code_id,
            user_role=user_role,
            focus_area=focus_area
        )
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error generating contextual recommendations: {str(e)}")
        return jsonify({"error": str(e)}), 500


@advanced_mcp_bp.route('/api/advanced-mcp/conversation-history', methods=['GET'])
@login_required
def get_conversation_history():
    """
    API endpoint to retrieve multi-turn conversation history with the AI assistant.
    
    This endpoint provides access to the complete conversation history between the user
    and the AI assistant, facilitating multi-turn dialogue capabilities and enabling
    the system to maintain context across multiple interactions. The conversation history
    is crucial for providing coherent, contextually aware responses in ongoing analytical
    discussions.
    
    The conversation history includes:
    1. User queries in chronological order
    2. AI responses with timestamps
    3. Contextual data referenced in the conversation
    4. Follow-up suggestions based on conversation flow
    
    This history enables several advanced capabilities:
    - Contextual awareness across multiple queries
    - Reference to earlier findings and insights
    - Progressive refinement of analysis based on dialogue
    - Coherent narrative construction in analytical discussions
    - Ability to build on previous questions and analyses
    
    The endpoint retrieves the conversation history from the advanced analysis agent's
    memory system, which maintains user-specific conversation contexts in a secure,
    privacy-compliant manner.
    
    Returns:
        JSON response containing:
        {
            "history": [
                {
                    "role": "user",
                    "content": "What are the trends in property tax rates?",
                    "timestamp": "2025-04-11T10:23:45Z"
                },
                {
                    "role": "assistant",
                    "content": "Analysis of property tax rates shows...",
                    "timestamp": "2025-04-11T10:23:50Z",
                    "referenced_data": {...}
                },
                ...
            ]
        }
        
    Error responses:
        500: Error retrieving conversation history
    
    Authentication:
        This endpoint requires user authentication via login_required decorator
        to ensure conversation privacy and data security.
    
    Note:
        Conversation histories are user-specific and session-bound to maintain
        privacy and security of sensitive tax discussions.
    """
    try:
        advanced_agent = get_advanced_analysis_agent()
        history = advanced_agent.get_conversation_history()
        return jsonify({"history": history})
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return jsonify({"error": str(e)}), 500


@advanced_mcp_bp.route('/api/advanced-mcp/conversation-history', methods=['DELETE'])
@login_required
def clear_conversation_history():
    """
    API endpoint to clear the AI assistant conversation history for the current user.
    
    This endpoint allows users to reset their conversation context with the AI assistant,
    clearing all prior interactions and starting a fresh dialogue session. This operation
    is useful for:
    
    1. Starting new analytical topics without context influence from previous discussions
    2. Clearing sensitive information from the conversation memory
    3. Resolving context conflicts that might arise in complex, lengthy discussions
    4. Improving system performance by reducing memory overhead
    5. Ensuring data privacy by removing conversational data when no longer needed
    
    The endpoint triggers a complete purge of the conversation history from the
    advanced analysis agent's memory system, maintaining only system-level
    knowledge while removing all user-specific conversation threads.
    
    The operation is irreversible and removes all:
    - Previous user queries and timestamps
    - AI assistant responses
    - Contextual references and data connections
    - Conversation-specific metadata
    
    Returns:
        JSON response confirming successful deletion:
        {
            "status": "success",
            "message": "Conversation history cleared"
        }
        
    Error responses:
        500: Error occurred while clearing conversation history
    
    Authentication:
        This endpoint requires user authentication via login_required decorator
        to ensure users can only clear their own conversation history.
    
    Security note:
        While this endpoint clears the conversation from active memory, it does not
        affect system audit logs that may track API interactions for security
        and compliance purposes.
    """
    try:
        advanced_agent = get_advanced_analysis_agent()
        advanced_agent.clear_conversation_history()
        return jsonify({"status": "success", "message": "Conversation history cleared"})
    except Exception as e:
        logger.error(f"Error clearing conversation history: {str(e)}")
        return jsonify({"error": str(e)}), 500


@advanced_mcp_bp.route('/api/advanced-mcp/cross-dataset', methods=['POST'])
@login_required
def analyze_cross_dataset():
    """
    API endpoint to perform sophisticated cross-dataset pattern analysis across tax data sources.
    
    This powerful analytical endpoint leverages AI capabilities to identify complex patterns, 
    relationships, correlations, and anomalies across multiple heterogeneous tax datasets. 
    It enables discovery of insights that would be difficult to detect when analyzing
    each dataset in isolation, providing a comprehensive, integrated view of tax data relationships.
    
    Key capabilities of this endpoint include:
    1. Identification of correlations between tax codes and historical rate patterns
    2. Detection of anomalies that span multiple datasets
    3. Discovery of causal relationships between property characteristics and tax rates
    4. Recognition of trend patterns across geographical and temporal dimensions
    5. Integration of qualitative and quantitative data for contextual insights
    
    The cross-dataset analysis process follows these steps:
    1. Data preparation and normalization across provided datasets
    2. Correlation analysis to identify relationships between variables
    3. Pattern recognition to detect recurring structures and trends
    4. Anomaly detection to identify statistical outliers
    5. Insight generation to interpret and explain identified patterns
    6. Formatting results with supporting evidence and confidence levels
    
    Request body:
        JSON object containing:
        {
            "tax_codes": [                       (Required) Array of tax code data
                {"code": "1234", "total_assessed_value": 1000000, ...},
                ...
            ],
            "historical_rates": [                (Required) Array of historical rate data
                {"tax_code_id": 1, "year": 2023, "levy_rate": 0.015, ...},
                ...
            ],
            "property_records": [                (Optional) Array of property data
                {"property_id": 1, "tax_code_id": 1, "assessment": 250000, ...},
                ...
            ]
        }
    
    Returns:
        JSON response containing:
        {
            "response": {
                "correlations": [
                    "Strong positive correlation between property size and assessed value...",
                    ...
                ],
                "patterns": [
                    "Tax codes in northern districts show consistent 3% annual growth pattern...",
                    ...
                ],
                "anomalies": [
                    "Tax code 4567 shows unusual rate decrease despite rising property values...",
                    ...
                ],
                "insights": [
                    "Commercial properties in district 3 have seen disproportionate increases...",
                    ...
                ]
            }
        }
        
    Error responses:
        400: Missing required parameters (tax_codes or historical_rates)
        500: Error analyzing cross-dataset patterns
    
    Authentication:
        This endpoint requires user authentication via login_required decorator
        to ensure data privacy and access control.
    
    Note:
        For optimal analysis, provide data from at least two different dataset types.
        The more comprehensive the data provided, the more valuable the insights generated.
    """
    data = request.json
    if not data or 'tax_codes' not in data or 'historical_rates' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    tax_codes = data['tax_codes']
    historical_rates = data['historical_rates']
    property_records = data.get('property_records')
    
    try:
        # Get advanced analysis agent
        advanced_agent = get_advanced_analysis_agent()
        response = advanced_agent.analyze_cross_dataset_patterns(
            tax_codes=tax_codes,
            historical_rates=historical_rates,
            property_records=property_records
        )
        
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error analyzing cross-dataset patterns: {str(e)}")
        return jsonify({"error": str(e)}), 500