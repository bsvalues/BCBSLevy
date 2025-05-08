"""
Simple Claude API Client.

This module provides a minimal Claude API client implementation that
works around the known issues with the official Anthropic client.
It uses low-level HTTP requests to avoid the problematic proxies parameter.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class SimpleClaudeClient:
    """
    Lightweight wrapper for the Claude API that avoids the problematic Anthropic client.
    
    This class provides a simplified interface to communicate with Claude
    while avoiding the initialization issues in the official client.
    It uses direct HTTP requests to interact with the Claude API.
    
    The class is designed to mimic the official Anthropic client interface
    to ensure compatibility with existing code.
    """
    
    class MessagesAPI:
        """Nested class to mimic the Anthropic client's messages attribute."""
        
        def __init__(self, parent):
            self.parent = parent
        
        def create(self, model: str, messages: list, system=None, max_tokens: int = 1000, 
                  temperature: float = 0.7, **kwargs) -> dict:
            """
            Create a message via the Claude API, matching the official client's interface.
            
            Args:
                model: The Claude model to use
                messages: List of message objects with 'role' and 'content'
                system: Optional system prompt
                max_tokens: Maximum tokens in response
                temperature: Sampling temperature (0-1)
                
            Returns:
                Response object that matches the structure from the official client
            """
            # Delegate to the parent's generate_message method
            return self.parent.generate_message(
                messages=messages, 
                system=system, 
                max_tokens=max_tokens, 
                temperature=temperature,
                model=model
            )
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude client with API key validation.
        
        Args:
            api_key: The Anthropic API key. If not provided, will try to get from env var.
        """
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set the ANTHROPIC_API_KEY environment variable.")
        
        # Claude API endpoint
        self.base_url = "https://api.anthropic.com/v1"
        
        # Set up the API version header that Claude requires
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        
        # Set up the messages API interface for compatibility with the official client
        self.messages = self.MessagesAPI(self)
        
        logger.info("SimpleClaudeClient initialized successfully")
    
    def generate_message(self, 
                        messages: List[Dict[str, str]], 
                        system: Optional[str] = None,
                        max_tokens: int = 1000,
                        temperature: float = 0.7,
                        model: str = "claude-3-5-sonnet-20241022") -> Dict[str, Any]:
        """
        Send a messages request to the Claude API.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            system: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            model: Claude model to use
            
        Returns:
            The API response as a dictionary
        """
        url = f"{self.base_url}/messages"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system:
            payload["system"] = system
        
        try:
            logger.info(f"Sending request to Claude API with {len(messages)} messages")
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            result = response.json()
            logger.info(f"Successfully received response from Claude API")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Claude API: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"API error details: {json.dumps(error_detail)}")
                except:
                    logger.error(f"API error status code: {e.response.status_code}")
            raise
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Simplified interface to generate text from a prompt.
        
        Args:
            prompt: The text prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            
        Returns:
            The generated text as a string
        """
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.generate_message(messages, max_tokens=max_tokens, temperature=temperature)
            
            # Extract the content from the response
            if "content" in response and len(response["content"]) > 0:
                content_blocks = response["content"]
                return content_blocks[0]["text"]
            
            return ""
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return f"Error: {str(e)}"