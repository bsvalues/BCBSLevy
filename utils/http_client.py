"""
HTTP Client utilities for the Levy Calculation System.

This module provides standardized HTTP client setup for various API integrations,
ensuring consistent configuration across different services.
"""

import logging
import os
from typing import Optional, Dict, Any

# Import our patch first to fix the Anthropic client
from utils.anthropic_patch import patch_anthropic

# Apply the patch before importing Anthropic
patch_applied = patch_anthropic()

# Now import the fixed Anthropic client
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
    
    # Validate API key format (skip for now to allow testing with any key)
    # if not api_key.startswith('sk-ant-'):
    #     logger.warning("Invalid Anthropic API key format. Keys should start with 'sk-ant-'")
    #     return None
    
    # Direct approach - define the class directly without using imports
    # This avoids any issues with module-level imports or inheritance
    try:
        logger.info("Creating Anthropic client using direct approach")
        
        # Direct monkey-patching approach to create the Anthropic client
        # This is a fallback approach to address the proxies parameter issue
        from anthropic import Anthropic as OriginalAnthropic
        
        # Print information about the class to help with debugging
        logger.info(f"Anthropic class: {OriginalAnthropic}")
        logger.info(f"Anthropic class initialization params: {OriginalAnthropic.__init__.__code__.co_varnames}")
        
        # Create a wrapper class that filters out problematic parameters
        class SafeAnthropic(OriginalAnthropic):
            def __init__(self, api_key, **kwargs):
                # Filter out problematic parameters
                safe_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ['proxies']}
                # Call the parent class constructor with safe parameters
                super().__init__(api_key=api_key, **safe_kwargs)
        
        # Create an instance of our safe class
        client = SafeAnthropic(api_key=api_key)
        logger.info("Successfully created Anthropic client using safe wrapper")
        return client
        
    except Exception as e:
        # Log detailed error info for debugging
        logger.error(f"Error creating Anthropic client using safe wrapper: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception args: {e.args}")
        
        # Try the most direct approach as a last resort
        try:
            logger.info("Attempting final fallback with minimal code")
            # Direct, minimal client creation with no extra parameters
            from anthropic import Anthropic as RawAnthropic
            client = RawAnthropic(api_key=api_key)
            logger.info("Successfully created Anthropic client using minimal approach")
            return client
        except Exception as e2:
            logger.error(f"All approaches to create Anthropic client failed: {str(e2)}")
            return None