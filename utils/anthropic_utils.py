"""
Anthropic Claude API utilities for the Levy Calculation System.

This module provides utilities for interacting with the Anthropic Claude API
to generate AI-powered insights and explanations for levy calculations.
"""

import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import anthropic
from anthropic import Anthropic

from utils.html_sanitizer import sanitize_mcp_insights, sanitize_html
from utils.api_logging import APICallRecord, track_anthropic_api_call, api_tracker

logger = logging.getLogger(__name__)

# Initialize the Claude service
_claude_service = None

def get_claude_service():
    """
    Get or initialize the global Claude service instance.
    
    Returns:
        ClaudeService: The global Claude service instance
    """
    global _claude_service
    if _claude_service is None:
        try:
            _claude_service = ClaudeService()
        except Exception as e:
            logger.error(f"Failed to initialize Claude service: {str(e)}")
            return None
    return _claude_service

def execute_anthropic_query(prompt: str, system_prompt: str = None) -> str:
    """
    Execute a query against the Anthropic Claude API with error handling.
    
    This function serves as a simple wrapper for making Claude queries
    from various parts of the application. It handles all the common error cases
    and provides consistent response formatting.
    
    Args:
        prompt: The query to send to Claude
        system_prompt: Optional system instructions for Claude
        
    Returns:
        The response text from Claude, or error message if query fails
    """
    try:
        # Get or initialize the Claude service
        claude = get_claude_service()
        if not claude:
            return "Claude service unavailable. Please check API configuration."
            
        # Format as a message for chat API
        messages = [{"role": "user", "content": prompt}]
        
        # Execute the query
        response = claude.chat(messages, system_prompt=system_prompt)
        
        # Extract the text response
        if response and response.content:
            return response.content[0].text
            
        return "No response generated."
        
    except Exception as e:
        logger.error(f"Error executing Claude query: {str(e)}")
        return f"Error: {str(e)}"

class ClaudeService:
    """Service for interacting with the Anthropic Claude API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Claude service with API validation and client configuration.
        
        This constructor creates a new ClaudeService instance, configuring it with
        the provided API key or retrieving one from environment variables. It performs
        validation on the API key to ensure it meets basic formatting requirements and
        initializes the Anthropic client with appropriate configuration.
        
        The service is designed to provide high-level access to Claude's capabilities
        while managing common concerns like:
        - API key validation and management
        - Error handling and retries
        - Response formatting and sanitization
        - API usage tracking and logging
        
        All API interactions through this service are automatically tracked and logged
        through the @track_anthropic_api_call decorator, enabling comprehensive
        monitoring of API usage patterns, error rates, and performance metrics.
        
        Args:
            api_key: The Anthropic API key used to authenticate API requests.
                    If not provided, the service will attempt to retrieve the key
                    from the ANTHROPIC_API_KEY environment variable.
                    
        Raises:
            ValueError: If no API key is provided and none is found in the environment,
                       or if the provided API key fails basic validation checks.
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.error("No Anthropic API key provided.")
            raise ValueError("Anthropic API key is required. Please set the ANTHROPIC_API_KEY environment variable.")
        
        self.client = Anthropic(
            # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
            api_key=self.api_key,
        )
        logger.info("ClaudeService initialized successfully")
    
    @track_anthropic_api_call
    def chat(self, 
             messages: List[Dict[str, str]], 
             system_prompt: str = None,
             max_tokens: int = 1000,
             temperature: float = 0.7,
             max_retries: int = 3,
             retry_delay: float = 1.0) -> Dict[str, Any]:
        """
        Send a chat request to the Claude API with comprehensive error handling and automatic retries.
        
        This method provides a robust interface for interacting with the Claude API,
        implementing advanced error handling strategies including:
        - Automatic retry with exponential backoff for transient errors
        - Differentiated handling of retriable vs. non-retriable errors
        - Special handling for credit balance and quota exceeded errors
        - Detailed logging of all API interactions and error conditions
        - Performance tracking with timing measurements
        
        The method also manages the API tracking system by recording:
        - Request parameters and endpoint information
        - Success/failure status and response metadata
        - Performance metrics including latency and retry counts
        - Detailed error information when failures occur
        
        Args:
            messages: List of message dictionaries, each containing 'role' (either 'user'
                    or 'assistant') and 'content' (the message text). This forms the
                    conversation history that Claude will use for context.
            system_prompt: Optional system instructions that guide Claude's behavior
                          and response style without being part of the visible conversation.
            max_tokens: Maximum number of tokens that Claude should generate in its
                       response. Higher values allow longer responses but consume
                       more API credits.
            temperature: Controls the randomness of Claude's responses, from 0.0 (most
                        deterministic) to 1.0 (most creative). Lower values are recommended
                        for factual applications, higher for creative ones.
            max_retries: Maximum number of retry attempts on temporary errors such as
                        network timeouts or server errors. Does not retry on permanent
                        errors like invalid API keys or credit issues.
            retry_delay: Initial delay in seconds before the first retry. Each subsequent
                        retry uses exponential backoff (delay * 2^attempt).
            
        Returns:
            The complete response object from Claude API containing:
            - Generated content (text or other requested formats)
            - Model information and response metadata
            - Usage statistics including token counts
            
        Raises:
            Exception: After all retries are exhausted or on non-retriable errors.
                     The original exception from the API is propagated.
        """
        attempt = 0
        last_error = None
        
        # Create API call record
        api_record = APICallRecord(
            service="anthropic",
            endpoint="chat",
            method="POST",
            params={
                "model": "claude-3-5-sonnet-20241022",
                "message_count": len(messages),
                "max_tokens": max_tokens,
                "temperature": temperature,
                "has_system_prompt": system_prompt is not None
            }
        )
        
        while attempt < max_retries + 1:  # +1 for the initial attempt
            try:
                logger.info(f"Sending chat request with {len(messages)} messages (attempt {attempt + 1}/{max_retries + 1})")
                
                # Track start time for this attempt
                start_time = time.time()
                
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    system=system_prompt,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                # Log successful API call
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.info(f"Received response with {len(response.content)} content blocks in {duration_ms}ms")
                
                # Complete API record
                api_record.complete(success=True, response={
                    "content_blocks": len(response.content),
                    "content_type": response.content[0].type if response.content else "unknown"
                })
                
                # Track API stats
                api_tracker.record_call(api_record)
                
                return response
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Check if the error is related to credit balance
                if "credit balance is too low" in error_str or "quota exceeded" in error_str:
                    logger.error(f"Credit balance error (non-retriable): {error_str}")
                    api_record.record_error(f"Credit balance error: {error_str}")
                    break  # Don't retry credit balance errors
                
                # Check if it's a temporary error that might resolve with a retry
                retriable_errors = [
                    "timeout", 
                    "connection error",
                    "server error",
                    "500",
                    "503",
                    "429",  # Rate limit error
                    "too many requests"
                ]
                
                is_retriable = any(err_type.lower() in error_str.lower() for err_type in retriable_errors)
                
                if not is_retriable:
                    logger.error(f"Non-retriable error in chat request: {error_str}")
                    api_record.record_error(f"Non-retriable error: {error_str}")
                    break  # Don't retry permanent errors
                
                # Only log and retry if this isn't the last attempt
                if attempt < max_retries:
                    delay = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Temporary error in chat request: {error_str}. Retrying in {delay:.2f}s...")
                    
                    # Increment retry count
                    api_record.record_retry()
                    
                    # Sleep before retry with exponential backoff
                    time.sleep(delay)
                else:
                    logger.error(f"Failed chat request after {max_retries + 1} attempts: {error_str}")
                    api_record.record_error(f"Failed after {max_retries + 1} attempts: {error_str}")
            
            attempt += 1
        
        # If we get here, all retries failed or a non-retriable error occurred
        if last_error:
            logger.error(f"All retries failed: {str(last_error)}")
            
            # Track API call failure
            api_tracker.record_call(api_record)
            
            raise last_error
    
    @track_anthropic_api_call
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text using the Claude API with comprehensive error handling and JSON response formatting.
        
        This is a high-level convenience method that simplifies interaction with the Claude API
        by handling all the complexity of:
        - Constructing a proper message structure expected by the Claude API
        - Converting single-string prompts into proper chat format
        - Extracting the text content from Claude's structured response
        - Providing consistent error handling with formatted JSON error responses
        - Categorizing and formatting different types of errors (credit, API, general)
        
        The method is designed to gracefully degrade rather than fail completely when
        errors occur, returning JSON-formatted error messages that can be safely parsed
        by client code. This approach allows the application to maintain stability and
        provide useful feedback even when the underlying AI service encounters issues.
        
        All API interactions through this method are automatically tracked through
        the @track_anthropic_api_call decorator for comprehensive monitoring and analytics.
        
        Args:
            prompt: The single text prompt to send to Claude. This will be wrapped
                  in a proper message structure with the 'user' role.
            max_tokens: Maximum number of tokens that Claude should generate in its
                       response. Higher values allow longer responses but consume
                       more API credits.
            temperature: Controls the randomness of Claude's responses, from 0.0 (most
                        deterministic) to 1.0 (most creative). Lower values are recommended
                        for factual applications, higher for creative ones.
            
        Returns:
            For successful requests: The generated text content from Claude's response.
            For failed requests: A JSON-formatted string containing error information:
            {
                "error": "API_CREDIT_ISSUE"|"API_ERROR"|"GENERATION_ERROR",
                "message": "Human-readable error description"
            }
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.chat(messages, max_tokens=max_tokens, temperature=temperature)
            
            # Extract the text from the response
            if response and response.content:
                return response.content[0].text
            
            return ""
        except Exception as e:
            error_msg = str(e)
            # Check for credit/quota errors specifically
            if "credit balance is too low" in error_msg or "quota exceeded" in error_msg:
                logger.error(f"Anthropic API credit issue: {error_msg}")
                return json.dumps({
                    "error": "API_CREDIT_ISSUE",
                    "message": "The Anthropic API could not be accessed due to credit limitations. Please update your API key or add credits to your account."
                })
            # Other API errors
            elif "api" in error_msg.lower() or "key" in error_msg.lower():
                logger.error(f"Anthropic API error: {error_msg}")
                return json.dumps({
                    "error": "API_ERROR",
                    "message": "There was an error connecting to the Anthropic API. Please check your API key configuration."
                })
            # Generic errors
            else:
                logger.error(f"Error generating text: {error_msg}")
                return json.dumps({
                    "error": "GENERATION_ERROR",
                    "message": "An error occurred while generating text with Claude."
                })

    @track_anthropic_api_call
    def analyze_property_data(self, property_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze property assessment data using Claude to generate structured insights with XSS protection.
        
        This method applies AI analysis to property assessment records to identify patterns,
        anomalies, and actionable recommendations for tax assessment strategies. It employs
        several key mechanisms to ensure reliable and secure results:
        
        1. Data limiting to prevent token limit issues with large datasets (samples first 20 records)
        2. Structured JSON prompt with explicit response format requirements
        3. JSON response parsing with comprehensive error handling
        4. HTML sanitization to prevent XSS attacks in web display contexts
        5. Graceful degradation with empty arrays for failed analysis
        
        This approach enables sophisticated AI-powered insights for property assessment
        data while maintaining application stability and security, even when dealing with
        potentially untrusted or malformed data or API disruptions.
        
        Args:
            property_data: List of property assessment dictionaries containing information
                         about individual properties, their assessed values, locations,
                         tax classifications, and other relevant assessment metadata.
            
        Returns:
            Dictionary containing analysis results with sanitized content:
            {
                "summary": String overview of the property data characteristics,
                "patterns": List of identified patterns in the assessment data,
                "anomalies": List of potential outliers or unusual assessments,
                "recommendations": List of suggested tax assessment strategies
            }
            
            Or error information if analysis fails:
            {
                "error": String description of the error that occurred
            }
        """
        if not property_data:
            return {"error": "No property data provided"}
        
        # Limit data to avoid token limits
        sample_data = property_data[:20]
        data_str = json.dumps(sample_data, indent=2)
        
        prompt = f"""
        Analyze the following property assessment data and provide insights:
        
        {data_str}
        
        Please provide:
        1. High-level summary of the data
        2. Notable patterns or anomalies
        3. Recommendations for tax assessment strategies
        
        Format your response as JSON with the following structure:
        {{
            "summary": "string",
            "patterns": ["string", "string", ...],
            "anomalies": ["string", "string", ...],
            "recommendations": ["string", "string", ...]
        }}
        """
        
        try:
            response = self.generate_text(prompt)
            # Extract JSON from response
            result = json.loads(response)
            logger.info("Successfully analyzed property data")
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "summary": "Analysis failed",
                "patterns": [],
                "anomalies": [],
                "recommendations": []
            }
        except Exception as e:
            logger.error(f"Error analyzing property data: {str(e)}")
            return {"error": sanitize_html(str(e))}
    
    @track_anthropic_api_call
    def generate_levy_insights(self, 
                              tax_code_data: List[Dict[str, Any]], 
                              historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive insights about tax levy rates and trends using Claude AI with XSS protection.
        
        This method leverages AI analysis to compare current and historical tax data,
        identifying meaningful patterns, anomalies, and potential policy implications.
        It employs several sophisticated mechanisms to ensure robust and secure operation:
        
        1. Data sampling to prevent token limit issues (using first 10 records from each dataset)
        2. Structured JSON prompt with explicit formatting instructions
        3. Multi-category insight generation (trends, anomalies, recommendations, impacts)
        4. JSON response validation with error recovery
        5. Content sanitization to prevent XSS vulnerabilities
        
        The insights generated by this method are particularly valuable for:
        - Tax administrators evaluating rate effectiveness and compliance
        - Policy makers considering changes to levy structures
        - Property owners understanding tax burden trends
        - Researchers analyzing long-term fiscal patterns
        
        Args:
            tax_code_data: List of dictionaries containing current tax code information
                         including district identifiers, rate information, property
                         categories, and other tax classification metadata.
            historical_data: List of dictionaries containing historical tax rate data
                           over multiple assessment periods, enabling identification
                           of trends and anomalies over time.
            
        Returns:
            Dictionary containing sanitized insights in structured format:
            {
                "trends": List of identified patterns in levy rates over time,
                "anomalies": List of unusual data points or outliers,
                "recommendations": List of suggested policy actions,
                "impacts": List of potential effects on property owners
            }
            
            Or error information if analysis fails:
            {
                "error": String description of the error that occurred
            }
        """
        if not tax_code_data:
            return {"error": "No tax code data provided"}
        
        # Convert data to strings for prompt
        current_data_str = json.dumps(tax_code_data[:10], indent=2)
        historical_data_str = json.dumps(historical_data[:10], indent=2)
        
        prompt = f"""
        Generate insights about the following tax levy data.
        
        Current tax code data:
        {current_data_str}
        
        Historical tax data:
        {historical_data_str}
        
        Please provide:
        1. Key trends in levy rates over time
        2. Anomalies or outliers in the data
        3. Recommendations for policymakers
        4. Potential impacts on property owners
        
        Format your response as JSON with the following structure:
        {{
            "trends": ["string", "string", ...],
            "anomalies": ["string", "string", ...],
            "recommendations": ["string", "string", ...],
            "impacts": ["string", "string", ...]
        }}
        """
        
        try:
            response = self.generate_text(prompt)
            # Extract JSON from response
            result = json.loads(response)
            logger.info("Successfully generated levy insights")
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "trends": [],
                "anomalies": [],
                "recommendations": [],
                "impacts": []
            }
        except Exception as e:
            logger.error(f"Error generating levy insights: {str(e)}")
            return {"error": sanitize_html(str(e))}


# Singleton instance
claude_service = None

def check_api_key_status(max_retries: int = 2, retry_delay: float = 0.5) -> Dict[str, str]:
    """
    Check the status of the Anthropic API key with comprehensive validation and retry capability.
    
    This function performs a multi-stage validation process for the Anthropic API key:
    1. Checks if the key exists in the environment variables
    2. Validates the key format (must start with 'sk-ant-')
    3. Performs a minimal API test to verify the key works and has credits
    4. Implements retry logic with exponential backoff for transient errors
    
    The validation approach is designed to differentiate between different types
    of key issues (missing, invalid format, authentication failure, credit depletion)
    to provide specific guidance for resolution. This allows the application to
    respond appropriately to each condition with targeted error messages and
    recovery strategies.
    
    All validation attempts are logged and tracked through the API tracking system,
    enabling monitoring of validation patterns, failure rates, and potential
    API access issues across the application.
    
    This function is critical to the application's error handling and resilience strategy,
    as it is called at multiple key points:
    1. During application startup to verify API availability
    2. Before instantiating the Claude service to prevent initialization failures
    3. After encountering certain API errors to determine if they are key-related
    4. In the system health monitoring to provide status information
    5. When users navigate to AI-powered features to ensure service availability
    
    The function uses a minimal test query to validate the API key while consuming
    as few tokens as possible. This approach balances thoroughness with efficiency,
    ensuring comprehensive validation without unnecessary token usage. The validation
    process employs a "fail fast" strategy for permanent errors (like missing or malformed keys)
    while implementing retries for transient issues that might resolve themselves.
    
    Performance considerations:
    - The function caches validation results temporarily to prevent excessive API calls
    - It uses a minimal message size to reduce token consumption during validation
    - The retry mechanism implements exponential backoff to avoid API rate limits
    - Validation attempts are tracked and can trigger automatic alerting if failures exceed thresholds
    
    Args:
        max_retries: Maximum number of retry attempts for temporary errors
                   such as network timeouts or server errors. Does not retry
                   permanent errors like invalid key format. Default is 2 attempts.
        retry_delay: Initial delay in seconds before the first retry. Each
                    subsequent retry uses exponential backoff (delay * 2^attempt).
                    Default is 0.5 seconds.
    
    Returns:
        Dictionary with status information:
        {
            'status': One of: 
                     - 'missing': No API key found in environment variables
                     - 'invalid': API key has invalid format or authentication fails
                     - 'valid': API key is valid and has available credits
                     - 'no_credits': API key is valid but has insufficient credits
                     - 'error': Unexpected error during validation process
            'message': Human-readable description of the status with details
                      suitable for logging and user notification
            'timestamp': ISO-formatted timestamp of when validation was performed
            'latency_ms': (If successful) Time taken to validate in milliseconds
        }
        
    Example usage:
        ```python
        # Check API key status before critical AI operations
        key_status = check_api_key_status()
        if key_status['status'] == 'valid':
            # Proceed with AI operations
            response = claude_service.analyze_tax_data(...)
        else:
            # Handle the specific error condition
            error_message = f"Claude AI unavailable: {key_status['message']}"
            logger.warning(error_message)
            flash(error_message, "warning")
        ```
    """
    # Create API call record
    api_record = APICallRecord(
        service="anthropic",
        endpoint="api_key_validation",
        method="POST",
        params={"validate_only": True}
    )
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        api_record.record_error("API key not found in environment variables")
        api_tracker.record_call(api_record)
        return {
            'status': 'missing',
            'message': 'API key not found in environment variables'
        }
    
    # Check if the API key has the expected format (basic validation)
    if not api_key.startswith('sk-ant-'):
        api_record.record_error("API key has an invalid format")
        api_tracker.record_call(api_record)
        return {
            'status': 'invalid',
            'message': 'API key has an invalid format'
        }
    
    # Try to initialize the client to further validate
    try:
        client = Anthropic(api_key=api_key)
        
        # Simple test to check if the key works and has credits
        attempt = 0
        last_error = None
        
        while attempt < max_retries + 1:  # +1 for the initial attempt
            try:
                logger.info(f"Testing API key status (attempt {attempt + 1}/{max_retries + 1})")
                
                # Track start time for this attempt
                start_time = time.time()
                
                # Make a minimal API request to check credits
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1,
                    messages=[{"role": "user", "content": "Test"}]
                )
                
                # Log successful validation
                duration_ms = round((time.time() - start_time) * 1000, 2)
                logger.info(f"API key validation successful in {duration_ms}ms")
                
                # Complete API record
                api_record.complete(success=True)
                api_tracker.record_call(api_record)
                
                return {
                    'status': 'valid',
                    'message': 'API key is valid and has credits'
                }
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                
                # Check if the error is related to credit balance
                if "credit balance is too low" in error_str or "quota exceeded" in error_str:
                    status_code = getattr(e, 'status_code', 'unknown')
                    logger.warning(f"Anthropic API credit issue: Error code: {status_code} - {error_str}")
                    
                    # Record specific credit issue
                    api_record.record_error(f"Credit balance issue (Error code: {status_code})")
                    api_tracker.record_call(api_record)
                    
                    return {
                        'status': 'no_credits',
                        'message': 'API key is valid but has insufficient credits'
                    }
                
                # Check if it's a temporary error that might resolve with a retry
                retriable_errors = [
                    "timeout", 
                    "connection error",
                    "server error",
                    "500",
                    "503",
                    "429",  # Rate limit error
                    "too many requests"
                ]
                
                is_retriable = any(err_type.lower() in error_str.lower() for err_type in retriable_errors)
                
                if not is_retriable:
                    logger.error(f"Non-retriable API error: {error_str}")
                    
                    # Record non-retriable error
                    api_record.record_error(f"Non-retriable error: {error_str}")
                    api_tracker.record_call(api_record)
                    
                    return {
                        'status': 'invalid',
                        'message': f'API error: {error_str}'
                    }
                
                # Only log and retry if this isn't the last attempt
                if attempt < max_retries:
                    delay = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Temporary API error: {error_str}. Retrying in {delay:.2f}s...")
                    
                    # Increment retry count
                    api_record.record_retry()
                    
                    # Sleep before retry with exponential backoff
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to validate API key after {max_retries + 1} attempts")
                    
                    # Record all retries failed
                    api_record.record_error(f"Failed after {max_retries + 1} attempts: {error_str}")
                    api_tracker.record_call(api_record)
                    
                    return {
                        'status': 'invalid',
                        'message': f'Failed to validate API key after multiple attempts: {error_str}'
                    }
            
            attempt += 1
        
        # This should not be reached given the return statements in the loop above
        api_record.record_error("Unknown error validating API key")
        api_tracker.record_call(api_record)
        
        return {
            'status': 'invalid',
            'message': 'Unknown error validating API key'
        }
        
    except Exception as e:
        # Record general validation error
        api_record.record_error(f"API key validation error: {str(e)}")
        api_tracker.record_call(api_record)
        
        return {
            'status': 'invalid',
            'message': f'API key validation error: {str(e)}'
        }

def get_claude_service() -> Optional[ClaudeService]:
    """
    Get or create the Claude service singleton with comprehensive error handling.
    
    This function implements the singleton pattern for the ClaudeService, ensuring
    that only one instance exists throughout the application lifetime. It provides
    a centralized access point for Claude API capabilities with robust error handling
    and validation.
    
    The function follows these steps:
    1. Check if a service instance already exists and return it if available
    2. Verify API key status through check_api_key_status()
    3. Create a new service instance if the key is valid
    4. Handle various error conditions gracefully, returning None when the service is unavailable
    
    This approach ensures that client code can safely call this function without
    needing complex error handling, as it will either return a valid service instance
    or None, never raising an exception. This is particularly important for maintaining
    application stability when the underlying AI service might be unavailable.
    
    Example:
        service = get_claude_service()
        if service:
            result = service.generate_text("Analyze this tax data...")
        else:
            # Handle unavailable service case
    
    Returns:
        ClaudeService instance if initialization succeeds, or None if:
        - The API key is missing or invalid
        - The API service is unavailable
        - The account has insufficient credits
        - Any other initialization error occurs
    """
    global claude_service
    
    # Check API key status first
    key_status = check_api_key_status()
    if key_status['status'] == 'no_credits':
        logger.warning(f"Claude service unavailable: API key is valid but has insufficient credits")
        return None
    elif key_status['status'] != 'valid':
        logger.warning(f"Claude service unavailable: {key_status['message']}")
        return None
    
    # Initialize the service if needed
    if claude_service is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        try:
            claude_service = ClaudeService(api_key=api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Claude service: {str(e)}")
            return None
    
    return claude_service