"""
HTTP Client utilities for the Levy Calculation System.

This module provides standardized HTTP client setup for various API integrations,
ensuring consistent configuration across different services.
"""

import logging
import os
from typing import Optional, Dict, Any

import anthropic
from anthropic import Anthropic

# Configure logging
logger = logging.getLogger(__name__)

def create_anthropic_client(api_key: Optional[str] = None) -> Optional[Anthropic]:
    """
    Create an Anthropic API client with proper configuration.
    
    This function creates an Anthropic client with the supplied API key or
    fetches one from the environment variables. It handles initialization
    errors gracefully and provides detailed logging.
    
    Args:
        api_key: Optional API key for authentication. If not provided,
                uses the ANTHROPIC_API_KEY environment variable.
                
    Returns:
        Anthropic client if successful, None if initialization fails.
    """
    # Use provided API key or get from environment
    api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
    
    if not api_key:
        logger.warning("No Anthropic API key provided or found in environment variables")
        return None
    
    # Validate API key format
    if not api_key.startswith('sk-ant-'):
        logger.warning("Invalid Anthropic API key format. Keys should start with 'sk-ant-'")
        return None
    
    try:
        # Create client with minimal parameters to avoid compatibility issues
        client = Anthropic(api_key=api_key)
        logger.info("Successfully created Anthropic client")
        return client
    except Exception as e:
        logger.error(f"Error creating Anthropic client: {str(e)}")
        return None