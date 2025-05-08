"""
Contextual Help Service: Provides AI-powered explanations for complex terms and visualizations.

This service implements a hybrid approach to generate contextual explanations:
1. Static pre-written explanations from official sources
2. Claude API for dynamic, context-aware explanations
3. OpenAI as a backup AI provider
4. Robust caching to minimize API calls

The service prioritizes authentic data from authoritative sources while providing
flexibility to generate explanations for new or uncommon terms.
"""
import os
import json
import logging
from datetime import datetime
import time
import pathlib

# Set up logging first so it's available for import handling
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the Claude API client
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available. Claude API will not be used.")

# Try to import OpenAI as a backup
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. OpenAI API will not be used as backup.")

# Initialize API clients
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Import our centralized client creator
try:
    from utils.http_client import create_anthropic_client
    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    HTTP_CLIENT_AVAILABLE = False
    logger.warning("HTTP client utility not available. Will use direct initialization.")

if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
    if HTTP_CLIENT_AVAILABLE:
        # Use the centralized client creator to avoid proxy issues
        logger.info("Using centralized HTTP client for Anthropic initialization")
        anthropic = create_anthropic_client(api_key=ANTHROPIC_API_KEY)
        if not anthropic:
            logger.error("Failed to create Anthropic client using HTTP client utility")
    else:
        # Fallback to direct initialization if HTTP client not available
        try:
            # Create minimal client with only the required api_key parameter
            anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
            logger.info("Successfully initialized Anthropic client directly")
        except Exception as e:
            anthropic = None
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
else:
    anthropic = None
    logger.warning("Anthropic API key not found. Claude API will not be used.")

if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    logger.warning("OpenAI API key not found. OpenAI API will not be used as backup.")

# Static explanation data file path
EXPLANATIONS_FILE = pathlib.Path("static/data/explanations.json")

# Define cache for storing generated explanations to reduce API calls
explanation_cache = {}

# Load static explanations from file
static_explanations = {}
try:
    if EXPLANATIONS_FILE.exists():
        with open(EXPLANATIONS_FILE, 'r') as f:
            static_explanations = json.load(f)
        logger.info(f"Loaded {len(static_explanations)} static explanations from {EXPLANATIONS_FILE}")
    else:
        logger.warning(f"Static explanations file {EXPLANATIONS_FILE} not found")
except Exception as e:
    logger.error(f"Error loading static explanations: {str(e)}")
    static_explanations = {}

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

def get_static_explanation(topic_id, user_role="analyst", context=None):
    """
    Get a pre-written explanation from the static database.
    
    Args:
        topic_id (str): The help topic identifier
        user_role (str): Role of the user (analyst, administrator, public)
        context (str, optional): Context about where this is being shown
        
    Returns:
        dict or None: Explanation dict if found, None otherwise
    """
    if topic_id in static_explanations:
        topic_info = get_topic_metadata(topic_id)
        explanation_data = static_explanations[topic_id]
        
        # Create a result structure similar to what the API would return
        result = {
            "topic_id": topic_id,
            "title": topic_info["title"],
            "explanation": explanation_data["full_explanation"],
            "category": topic_info["category"],
            "source": "static",
            "last_updated": explanation_data.get("last_updated", "Unknown"),
            "context": context,
            "user_role": user_role
        }
        
        logger.info(f"Retrieved static explanation for '{topic_id}'")
        return result
    
    return None

def generate_explanation_with_claude(topic_id, topic_info, context=None, additional_info=None, user_role="analyst"):
    """
    Generate explanation using the Claude API.
    
    Args:
        topic_id (str): The help topic identifier
        topic_info (dict): Topic metadata
        context (str, optional): Additional context about where this is being shown
        additional_info (dict, optional): Extra information to enhance the explanation
        user_role (str): Role of the user
        
    Returns:
        dict or None: Explanation dict if successful, None on failure
    """
    if not anthropic:
        logger.warning("Claude API is not available")
        return None
    
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
        # Add retry logic
        max_retries = 3
        retry_count = 0
        backoff_time = 1  # Start with 1 second backoff
        
        while retry_count < max_retries:
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
                    "source": "claude",
                    "context": context,
                    "user_role": user_role
                }
                
                logger.info(f"Generated explanation for '{topic_id}' with Claude API")
                return result
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Claude API attempt {retry_count} failed: {str(e)}")
                
                if retry_count < max_retries:
                    time.sleep(backoff_time)
                    backoff_time *= 2  # Exponential backoff
        
        logger.error(f"Claude API failed after {max_retries} attempts for topic '{topic_id}'")
        return None
        
    except Exception as e:
        logger.error(f"Error generating explanation with Claude for '{topic_id}': {str(e)}")
        return None

def generate_explanation_with_openai(topic_id, topic_info, context=None, additional_info=None, user_role="analyst"):
    """
    Generate explanation using the OpenAI API as a backup.
    
    Args:
        topic_id (str): The help topic identifier
        topic_info (dict): Topic metadata
        context (str, optional): Additional context about where this is being shown
        additional_info (dict, optional): Extra information to enhance the explanation
        user_role (str): Role of the user
        
    Returns:
        dict or None: Explanation dict if successful, None on failure
    """
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        logger.warning("OpenAI API is not available")
        return None
    
    system_content = """
    You are an expert property tax specialist providing clear, helpful explanations about tax levy concepts.
    Provide concise, accurate information in plain language with a helpful tone.
    Include relevant examples where appropriate and keep explanations under 250 words unless the topic is highly complex.
    Include 1-2 Washington State legal references (RCW citations) if applicable.
    """
    
    user_content = f"""
    Explain the term "{topic_info['title']}" in the context of property tax levy calculations.
    
    Context: {context or "General tax levy information"}
    User role: {user_role}
    Basic definition: {topic_info['short_desc']}
    
    Provide:
    1. A clear explanation of this concept
    2. How it's used in levy calculations
    3. Why it matters to the user
    """
    
    if additional_info:
        user_content += f"\n\nAdditional information:\n"
        for key, value in additional_info.items():
            user_content += f"- {key}: {value}\n"
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o", # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ],
            max_tokens=750
        )
        
        explanation_text = response.choices[0].message.content
        
        # Create result with metadata
        result = {
            "topic_id": topic_id,
            "title": topic_info["title"],
            "explanation": explanation_text,
            "category": topic_info["category"],
            "generated_at": datetime.utcnow().isoformat(),
            "source": "openai",
            "context": context,
            "user_role": user_role
        }
        
        logger.info(f"Generated explanation for '{topic_id}' with OpenAI API")
        return result
        
    except Exception as e:
        logger.error(f"Error generating explanation with OpenAI for '{topic_id}': {str(e)}")
        return None

def get_fallback_explanation(topic_id, topic_info, context=None, user_role="analyst"):
    """
    Get a basic fallback explanation when all other methods fail.
    
    Args:
        topic_id (str): The help topic identifier
        topic_info (dict): Topic metadata
        context (str, optional): Additional context about where this is being shown
        user_role (str): Role of the user
        
    Returns:
        dict: Basic explanation dict
    """
    fallback_text = f"""
    **{topic_info['title']}** - {topic_info['short_desc']}
    
    This term is used in property tax levy calculations in Washington state. 
    For more detailed information, please refer to the Washington State Department of Revenue
    property tax publications or consult with your local county assessor's office.
    """
    
    # Create result with metadata
    result = {
        "topic_id": topic_id,
        "title": topic_info["title"],
        "explanation": fallback_text,
        "category": topic_info["category"],
        "generated_at": datetime.utcnow().isoformat(),
        "source": "fallback",
        "context": context,
        "user_role": user_role
    }
    
    logger.info(f"Using fallback explanation for '{topic_id}'")
    return result

def generate_explanation(topic_id, context=None, additional_info=None, user_role="analyst"):
    """
    Generate a contextual explanation using a hybrid approach.
    
    This function implements a hierarchical data source strategy:
    1. Check cache first to avoid duplicate processing
    2. Use static pre-written explanations when available
    3. Try Claude API as the primary AI service
    4. Fall back to OpenAI API if Claude fails
    5. Provide a minimal fallback explanation as last resort
    
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
    
    # 1. Try to get static explanation first
    result = get_static_explanation(topic_id, user_role, context)
    
    # 2. If no static explanation, try Claude API
    if not result and anthropic:
        result = generate_explanation_with_claude(topic_id, topic_info, context, additional_info, user_role)
    
    # 3. If Claude fails, try OpenAI API as backup
    if not result and OPENAI_AVAILABLE and OPENAI_API_KEY:
        result = generate_explanation_with_openai(topic_id, topic_info, context, additional_info, user_role)
    
    # 4. If all else fails, use a fallback explanation
    if not result:
        result = get_fallback_explanation(topic_id, topic_info, context, user_role)
    
    # Cache the result regardless of source
    explanation_cache[cache_key] = result
    
    return result

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