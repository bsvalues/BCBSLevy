"""
Anthropic API Client patch to fix initialization issues.

This module monkey-patches the Anthropic client to fix compatibility
issues with the proxies parameter and other initialization problems.
"""

import logging
import importlib.util
import sys
from types import ModuleType

# Configure logging
logger = logging.getLogger(__name__)

def patch_anthropic():
    """
    Apply monkey patch to fix the Anthropic client initialization issues.
    
    This function uses a low-level approach to fix the proxies parameter issue
    by replacing the Anthropic.__init__ method with a custom version that
    filters out problematic parameters.
    
    Returns:
        bool: True if the patch was applied successfully, False otherwise
    """
    try:
        logger.info("Attempting to patch Anthropic client")
        
        # Check if anthropic module is already imported
        if "anthropic" in sys.modules:
            anthropic_module = sys.modules["anthropic"]
        else:
            # Dynamically import anthropic module
            spec = importlib.util.find_spec("anthropic")
            if not spec:
                logger.error("Failed to find anthropic module")
                return False
                
            anthropic_module = importlib.util.module_from_spec(spec)
            sys.modules["anthropic"] = anthropic_module
            spec.loader.exec_module(anthropic_module)
        
        # Get the Anthropic class
        AnthropicClass = getattr(anthropic_module, "Anthropic")
        
        # Store the original init method
        original_init = AnthropicClass.__init__
        
        # Define the patched init method
        def patched_init(self, api_key=None, **kwargs):
            """Patched __init__ method that filters out problematic parameters."""
            # Remove problematic parameters
            safe_kwargs = {k: v for k, v in kwargs.items() 
                          if k not in ['proxies']}
            
            # Call the original init with safe parameters
            original_init(self, api_key=api_key, **safe_kwargs)
        
        # Apply the monkey patch
        AnthropicClass.__init__ = patched_init
        
        logger.info("Successfully applied Anthropic client patch")
        return True
        
    except Exception as e:
        logger.error(f"Failed to patch Anthropic client: {str(e)}")
        return False