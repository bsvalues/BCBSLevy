"""
Contextual Help Service: Provides AI-powered explanations for complex terms and visualizations.

This service interfaces with the MCP framework and Claude API to generate
contextual explanations and help text for the TerraFusion platform.
"""
import os
import json
import logging
from datetime import datetime

# Import the Claude API client
from anthropic import Anthropic

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Anthropic client with API key
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

# Define cache for storing generated explanations to reduce API calls
explanation_cache = {}

# Define contextual help topics and their descriptions for the UI
HELP_TOPICS = {
    "levy_rate": {
        "title": "Levy Rate",
        "short_desc": "Tax rate per $1,000 of assessed property value",
        "category": "calculation"
    },
    "assessed_value": {
        "title": "Assessed Value",
        "short_desc": "Official valuation of property for tax purposes",
        "category": "property"
    },
    "levy_amount": {
        "title": "Levy Amount",
        "short_desc": "Total tax revenue collected by a district",
        "category": "calculation"
    },
    "new_construction": {
        "title": "New Construction",
        "short_desc": "Value of newly built properties added to tax rolls",
        "category": "adjustment"
    },
    "annexation": {
        "title": "Annexation",
        "short_desc": "Process of incorporating new areas into a district",
        "category": "adjustment"
    },
    "refund_levy": {
        "title": "Refund Levy",
        "short_desc": "Additional levy amount to cover tax refunds",
        "category": "adjustment"
    },
    "levy_limit": {
        "title": "Levy Limit",
        "short_desc": "Maximum allowable tax increase (typically 1%)",
        "category": "limit"
    },
    "statutory_limit": {
        "title": "Statutory Limit",
        "short_desc": "Legal maximum levy rate for a district type",
        "category": "limit"
    },
    "levy_worksheet": {
        "title": "Levy Worksheet",
        "short_desc": "Official form for calculating allowable levy amounts",
        "category": "document"
    },
    "regular_levy": {
        "title": "Regular Levy",
        "short_desc": "Standard property tax levy subject to statutory limits",
        "category": "calculation"
    },
    "excess_levy": {
        "title": "Excess Levy",
        "short_desc": "Special voted levy that exceeds regular levy limits",
        "category": "calculation"
    },
    "highest_lawful_levy": {
        "title": "Highest Lawful Levy",
        "short_desc": "Maximum levy amount allowed by law",
        "category": "limit"
    },
    "levy_rate_chart": {
        "title": "Levy Rate Chart",
        "short_desc": "Bar chart comparing tax rates across districts",
        "category": "visualization"
    },
    "levy_amount_chart": {
        "title": "Levy Amount Chart",
        "short_desc": "Bar chart comparing total tax revenue across districts",
        "category": "visualization"
    },
    "tax_code_area": {
        "title": "Tax Code Area",
        "short_desc": "Geographic area with unique combination of taxing districts",
        "category": "geography"
    }
}

def get_help_topics():
    """Return all available help topics with their metadata."""
    return HELP_TOPICS

def get_topic_metadata(topic_id):
    """Get metadata for a specific help topic."""
    if topic_id in HELP_TOPICS:
        return HELP_TOPICS[topic_id]
    else:
        logger.warning(f"Help topic '{topic_id}' not found")
        return {
            "title": topic_id.replace("_", " ").title(),
            "short_desc": "No description available",
            "category": "other"
        }

def generate_explanation(topic_id, context=None, additional_info=None, user_role="analyst"):
    """
    Generate a contextual explanation using the Claude API.
    
    Args:
        topic_id (str): The help topic identifier
        context (str, optional): Additional context about where this is being shown
        additional_info (dict, optional): Extra information to enhance the explanation
        user_role (str, optional): Role of the user (analyst, administrator, public)
        
    Returns:
        dict: Explanation text along with metadata
    """
    # Check cache first to avoid duplicate API calls
    cache_key = f"{topic_id}_{user_role}_{context or 'default'}"
    if cache_key in explanation_cache:
        logger.info(f"Returning cached explanation for '{topic_id}'")
        return explanation_cache[cache_key]
    
    # Get topic metadata
    topic_info = get_topic_metadata(topic_id)
    
    # Construct the prompt for Claude
    system_prompt = """
    You are an expert property tax specialist providing clear, helpful explanations about tax levy concepts.
    Follow these guidelines:
    1. Provide concise, accurate information in plain language
    2. Use a friendly, helpful tone appropriate for tax professionals
    3. Include relevant examples where appropriate
    4. Tailor the explanation to the user's role and the context where it appears
    5. For complex topics, provide a brief summary followed by more detailed information
    6. Format output with Markdown for readability (bold for key terms, bullet points for lists)
    7. Keep explanations under 250 words unless the topic is highly complex
    8. Include 1-2 relevant Washington State legal references if applicable (RCW citations)
    """
    
    user_prompt = f"""
    I need an explanation for the term **{topic_info['title']}** in the context of property tax levy calculations.
    
    Context where this appears: {context or "General tax levy information"}
    User role: {user_role}
    
    Basic definition: {topic_info['short_desc']}
    
    Please provide:
    1. A clear, concise explanation of this concept
    2. How it's used in levy calculations
    3. Why it matters to the user
    """
    
    if additional_info:
        user_prompt += f"\n\nAdditional information:\n"
        for key, value in additional_info.items():
            user_prompt += f"- {key}: {value}\n"
    
    try:
        # Call Claude API
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=750,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Extract and process the explanation
        explanation_text = response.content[0].text
        
        # Create result with metadata
        result = {
            "topic_id": topic_id,
            "title": topic_info["title"],
            "explanation": explanation_text,
            "category": topic_info["category"],
            "generated_at": datetime.utcnow().isoformat(),
            "context": context,
            "user_role": user_role
        }
        
        # Cache the result
        explanation_cache[cache_key] = result
        logger.info(f"Generated explanation for '{topic_id}'")
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating explanation for '{topic_id}': {str(e)}")
        return {
            "topic_id": topic_id,
            "title": topic_info["title"],
            "explanation": f"Sorry, we couldn't generate an explanation for {topic_info['title']} at this time. "
                          f"Please try again later or contact support.",
            "error": str(e),
            "category": topic_info["category"]
        }

def get_explanation_for_chart(chart_type, data_context=None, user_role="analyst"):
    """
    Generate an explanation specifically for a data visualization chart.
    
    Args:
        chart_type (str): Type of chart (levy_rate_chart, levy_amount_chart, etc.)
        data_context (dict, optional): Data context about what's being shown
        user_role (str): Role of the user
        
    Returns:
        dict: Chart explanation with interpretation guidance
    """
    # Add chart-specific context
    additional_info = {
        "explanation_type": "chart_interpretation",
        "chart_data_summary": json.dumps(data_context) if data_context else "No data provided"
    }
    
    context = "Data visualization to help understand tax levy patterns and comparisons"
    
    return generate_explanation(chart_type, context, additional_info, user_role)

def get_bulk_explanations(topic_ids, context=None, user_role="analyst"):
    """
    Generate explanations for multiple topics at once.
    
    Args:
        topic_ids (list): List of topic identifiers
        context (str, optional): Shared context for all explanations
        user_role (str): Role of the user
        
    Returns:
        dict: Dictionary of topic_id to explanation mappings
    """
    results = {}
    for topic_id in topic_ids:
        results[topic_id] = generate_explanation(topic_id, context, None, user_role)
    return results