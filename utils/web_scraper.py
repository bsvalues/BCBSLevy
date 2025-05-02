"""
Web scraping utilities for importing data from online sources.

This module provides functions to:
- Scrape data from websites using Trafilatura
- Extract structured data from HTML
- Parse and normalize extracted content
- Convert web data to importable formats
"""

import logging
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from urllib.parse import urlparse, parse_qs

import trafilatura
import pandas as pd
import requests
from bs4 import BeautifulSoup

from app import db
from models import ImportLog, ImportType

# Configure logging
logger = logging.getLogger(__name__)


def get_website_text_content(url: str) -> str:
    """
    Extract the main text content from a website.
    
    Args:
        url: The URL of the website to scrape
        
    Returns:
        Extracted text content from the website
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.error(f"Failed to download content from {url}")
            return ""
            
        # Extract the main content
        text = trafilatura.extract(downloaded)
        if not text:
            logger.warning(f"No text content extracted from {url}")
            return ""
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {url}: {str(e)}")
        return ""


def extract_tabular_data(url: str, table_index: int = 0) -> Optional[pd.DataFrame]:
    """
    Extract tabular data from a website.
    
    Args:
        url: The URL of the website containing tables
        table_index: The index of the table to extract (default: 0, the first table)
        
    Returns:
        DataFrame containing the extracted table data, or None if extraction fails
    """
    try:
        # Send a request to the website
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Use pandas to extract tables
        tables = pd.read_html(response.content)
        if not tables or len(tables) <= table_index:
            logger.warning(f"No tables found at index {table_index} on {url}")
            return None
            
        return tables[table_index]
    except Exception as e:
        logger.error(f"Error extracting table from {url}: {str(e)}")
        return None


def save_scraped_data(data: Union[str, pd.DataFrame], source_url: str, 
                     data_type: str, user_id: Optional[int] = None) -> Optional[str]:
    """
    Save scraped data to a file and create an import log.
    
    Args:
        data: The scraped data (text or DataFrame)
        source_url: The URL source of the data
        data_type: Type of data being saved ('text', 'table', etc.)
        user_id: ID of the user who initiated the scraping
        
    Returns:
        Path to the saved file, or None if saving fails
    """
    try:
        # Create directory for scraped data if it doesn't exist
        os.makedirs('scraped_data', exist_ok=True)
        
        # Generate filename based on URL and timestamp
        parsed_url = urlparse(source_url)
        domain = parsed_url.netloc
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scraped_{domain.replace('.', '_')}_{timestamp}"
        
        file_path = None
        if isinstance(data, pd.DataFrame):
            # Save DataFrame to CSV
            file_path = os.path.join('scraped_data', f"{filename}.csv")
            data.to_csv(file_path, index=False)
        elif isinstance(data, str):
            # Save text to file
            file_path = os.path.join('scraped_data', f"{filename}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
        else:
            logger.error(f"Unsupported data type: {type(data)}")
            return None
        
        # Create import log
        import_type = ImportType.OTHER  # Default to OTHER
        try:
            metadata = {
                'source_url': source_url,
                'data_type': data_type,
                'scrape_timestamp': timestamp,
                'domain': domain
            }
            
            # Create an import log entry
            import_log = ImportLog(
                filename=os.path.basename(file_path),
                import_type=import_type,
                user_id=user_id,
                year=datetime.now().year,  # Default to current year
                status="COMPLETED",
                import_metadata=metadata
            )
            db.session.add(import_log)
            db.session.commit()
            
            logger.info(f"Created import log entry for scraped data: {import_log.id}")
        except Exception as e:
            logger.error(f"Error creating import log: {str(e)}")
            # Continue even if logging fails
        
        return file_path
    except Exception as e:
        logger.error(f"Error saving scraped data: {str(e)}")
        return None


def scrape_mlb_scores(date_str: str) -> Optional[pd.DataFrame]:
    """
    Scrape MLB scores for a specific date.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        DataFrame containing the MLB scores, or None if scraping fails
    """
    url = f"https://www.mlb.com/scores/{date_str}"
    try:
        # First try to get the tabular data
        data = extract_tabular_data(url)
        if data is not None and not data.empty:
            return data
            
        # If tabular extraction fails, get the text content
        text = get_website_text_content(url)
        if not text:
            logger.warning(f"No content found at {url}")
            return None
            
        # Parse the text to extract game scores
        # This is a simple pattern matching approach - in a real implementation
        # you would need more robust parsing based on the actual page structure
        games = []
        for line in text.split('\n'):
            # Look for lines that might contain game scores
            match = re.search(r'([A-Za-z ]+) (\d+), ([A-Za-z ]+) (\d+)', line)
            if match:
                team1, score1, team2, score2 = match.groups()
                games.append({
                    'team1': team1.strip(),
                    'score1': int(score1),
                    'team2': team2.strip(),
                    'score2': int(score2),
                    'date': date_str
                })
        
        if games:
            return pd.DataFrame(games)
        else:
            logger.warning(f"No game scores extracted from {url}")
            return None
    except Exception as e:
        logger.error(f"Error scraping MLB scores: {str(e)}")
        return None


def scrape_and_import(url: str, data_type: str = 'text', 
                     user_id: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Scrape data from a URL and prepare it for import.
    
    Args:
        url: The URL to scrape
        data_type: Type of data to scrape ('text', 'table', 'mlb')
        user_id: ID of the user who initiated the scraping
        year: Tax year to associate with the data
        
    Returns:
        Dictionary containing scraping results
    """
    result = {
        'success': False,
        'message': '',
        'file_path': None,
        'record_count': 0
    }
    
    try:
        if not year:
            year = datetime.now().year
            
        data = None
        if data_type == 'text':
            data = get_website_text_content(url)
            if not data:
                result['message'] = f"No text content found at {url}"
                return result
                
            result['record_count'] = len(data.split('\n'))
        elif data_type == 'table':
            data = extract_tabular_data(url)
            if data is None or data.empty:
                result['message'] = f"No tabular data found at {url}"
                return result
                
            result['record_count'] = len(data)
        elif data_type == 'mlb':
            # Extract date from URL or use today's date
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', url)
            if date_match:
                date_str = date_match.group(1)
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')
                
            data = scrape_mlb_scores(date_str)
            if data is None or data.empty:
                result['message'] = f"No MLB scores found for {date_str}"
                return result
                
            result['record_count'] = len(data)
        else:
            result['message'] = f"Unsupported data type: {data_type}"
            return result
            
        # Save the scraped data
        file_path = save_scraped_data(data, url, data_type, user_id)
        if not file_path:
            result['message'] = "Failed to save scraped data"
            return result
            
        result['success'] = True
        result['message'] = f"Successfully scraped data from {url}"
        result['file_path'] = file_path
        
        return result
    except Exception as e:
        logger.error(f"Error during scraping and import: {str(e)}")
        result['message'] = f"Scraping error: {str(e)}"
        return result