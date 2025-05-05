"""
Web Scraper Demo Script

This standalone script demonstrates the web scraping capabilities that can be 
integrated into the LevyMaster system. It shows how to extract text content and
tabular data from websites.

Usage:
    python web_scraper_demo.py [url] [data_type]

Arguments:
    url - The URL to scrape (default: example URL)
    data_type - 'text', 'table', or 'mlb' (default: text)
"""

import sys
import os
import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import trafilatura
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create directory for scraped data
os.makedirs('scraped_data', exist_ok=True)


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


def extract_tabular_data(url: str, table_index: int = 0) -> pd.DataFrame:
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


def scrape_mlb_scores(date_str: str) -> pd.DataFrame:
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


def save_scraped_data(data, source_url: str, data_type: str) -> str:
    """
    Save scraped data to a file.
    
    Args:
        data: The scraped data (text or DataFrame)
        source_url: The URL source of the data
        data_type: Type of data being saved ('text', 'table', etc.)
        
    Returns:
        Path to the saved file, or None if saving fails
    """
    try:
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
            logger.info(f"DataFrame saved to {file_path}")
        elif isinstance(data, str):
            # Save text to file
            file_path = os.path.join('scraped_data', f"{filename}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
            logger.info(f"Text content saved to {file_path}")
        else:
            logger.error(f"Unsupported data type: {type(data)}")
            return None
        
        return file_path
    except Exception as e:
        logger.error(f"Error saving scraped data: {str(e)}")
        return None


def main():
    """Main function to demonstrate web scraping functionality."""
    # Set default values
    url = "https://en.wikipedia.org/wiki/Web_scraping"
    data_type = "text"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        data_type = sys.argv[2]
    
    logger.info(f"Starting web scraping demo for {url} with data type {data_type}")
    
    # Perform the scraping based on data type
    if data_type == "text":
        logger.info("Extracting text content from website...")
        data = get_website_text_content(url)
        if data:
            logger.info(f"Successfully extracted {len(data)} characters of text")
            logger.info(f"Preview: {data[:200]}...")
            
            # Save the data
            file_path = save_scraped_data(data, url, data_type)
            if file_path:
                logger.info(f"Text content saved to {file_path}")
        else:
            logger.error("Failed to extract text content")
            
    elif data_type == "table":
        logger.info("Extracting tabular data from website...")
        data = extract_tabular_data(url)
        if data is not None and not data.empty:
            logger.info(f"Successfully extracted table with {len(data)} rows and {len(data.columns)} columns")
            logger.info("Table preview:")
            logger.info(data.head(5))
            
            # Save the data
            file_path = save_scraped_data(data, url, data_type)
            if file_path:
                logger.info(f"Table data saved to {file_path}")
        else:
            logger.error("Failed to extract tabular data")
            
    elif data_type == "mlb":
        # Extract date from URL or use today's date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', url)
        if date_match:
            date_str = date_match.group(1)
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"Extracting MLB scores for {date_str}...")
        data = scrape_mlb_scores(date_str)
        if data is not None and not data.empty:
            logger.info(f"Successfully extracted {len(data)} game scores")
            logger.info("Scores preview:")
            logger.info(data)
            
            # Save the data
            file_path = save_scraped_data(data, url, data_type)
            if file_path:
                logger.info(f"MLB scores saved to {file_path}")
        else:
            logger.error("Failed to extract MLB scores")
            
    else:
        logger.error(f"Unsupported data type: {data_type}")
        logger.info("Supported data types: text, table, mlb")
        return
    
    logger.info("Web scraping demo completed")


if __name__ == "__main__":
    main()