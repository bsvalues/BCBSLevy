import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check template directory
try:
    template_dir = os.path.join(os.getcwd(), 'templates')
    print(f"Checking template directory: {template_dir}")
    if os.path.exists(template_dir):
        print(f"Template directory exists: {template_dir}")
        print("Templates found:")
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    print(f"  - {os.path.join(root, file)}")
    else:
        print(f"Template directory does not exist: {template_dir}")
except Exception as e:
    print(f"Error checking template directory: {str(e)}")

# Try to import Flask and other dependencies to check for issues
try:
    print("\nChecking imports:")
    import flask
    print(f"Flask version: {flask.__version__}")
    
    import trafilatura
    print(f"Trafilatura imported successfully")
    
    import sqlalchemy
    print(f"SQLAlchemy version: {sqlalchemy.__version__}")
    
    from models import db, ScrapeRequest, ScrapedContent
    print("Models imported successfully")
    
except ImportError as e:
    print(f"Import error: {str(e)}")
except Exception as e:
    print(f"Error during imports: {str(e)}")

# Check if routes_webscraper.py exists
try:
    webscraper_path = os.path.join(os.getcwd(), 'routes_webscraper.py')
    print(f"\nChecking webscraper blueprint file: {webscraper_path}")
    if os.path.exists(webscraper_path):
        print(f"Webscraper blueprint file exists")
        with open(webscraper_path, 'r') as f:
            first_lines = [f.readline() for _ in range(20)]
            print("First 20 lines of routes_webscraper.py:")
            for line in first_lines:
                print(f"  {line.rstrip()}")
    else:
        print(f"Webscraper blueprint file does not exist")
except Exception as e:
    print(f"Error checking webscraper blueprint: {str(e)}")