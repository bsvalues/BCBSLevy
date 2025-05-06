"""
Web Scraper utility functions.

This module provides functions for scraping web content using trafilatura.
"""

import trafilatura


def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and is easier to understand
    than raw HTML.
    
    Args:
        url: The URL of the website to scrape
        
    Returns:
        str: The extracted text content
        
    Raises:
        Exception: If there's an error fetching or parsing the content
    
    Some common websites to crawl information from:
    MLB scores: https://www.mlb.com/scores/YYYY-MM-DD
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            raise Exception(f"Failed to download content from {url}")
            
        # Extract the text content
        text = trafilatura.extract(downloaded)
        
        if not text:
            raise Exception(f"No text content could be extracted from {url}")
            
        return text
        
    except Exception as e:
        # Log the error and re-raise it
        print(f"Error scraping {url}: {str(e)}")
        raise