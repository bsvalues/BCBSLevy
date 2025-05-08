"""
HTTP Client utilities for the Levy Calculation System.

This module provides standardized HTTP client setup for various API integrations,
ensuring consistent configuration across different services.
"""

import logging
import os
from typing import Optional, Dict, Any, Union

# Import our simplified Claude client
from utils.simple_claude_client import SimpleClaudeClient

# This is needed for type hints but we won't use it directly
# to avoid the problematic initialization
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

def create_anthropic_client(api_key: Optional[str] = None) -> Optional[Union[SimpleClaudeClient, 'Anthropic']]:
    """
    Create a Claude API client with proper configuration.
    
    This function creates a SimpleClaudeClient instance with the supplied API key or
    fetches one from the environment variables. It handles initialization
    errors gracefully and provides detailed logging.
    
    The SimpleClaudeClient is a lightweight wrapper that avoids the problematic
    initialization issues in the official Anthropic client.
    
    Args:
        api_key: Optional API key for authentication. If not provided,
                uses the ANTHROPIC_API_KEY environment variable.
                
    Returns:
        SimpleClaudeClient instance if successful, None if initialization fails.
    """
    # Use provided API key or get from environment
    api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        logger.warning("No Anthropic API key provided or found in environment variables")
        return None
    
    try:
        logger.info("Creating SimpleClaudeClient")
        client = SimpleClaudeClient(api_key=api_key)
        logger.info("Successfully created SimpleClaudeClient")
        return client
    except Exception as e:
        logger.error(f"Error creating SimpleClaudeClient: {str(e)}")
        return None