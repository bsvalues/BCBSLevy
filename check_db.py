"""
Check database connectivity and schema.

This script checks if the database is accessible and returns basic information.
"""

import os
import logging
import sys
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_db_connection():
    """Check database connection and display information."""
    logger.info("Checking database connectivity...")
    
    # Get connection parameters from environment
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not found")
        return False
    
    logger.info(f"Using Database URL: {db_url}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Get database version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        logger.info(f"Database version: {version}")
        
        # Get table list
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        logger.info(f"Found {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Database connection test completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    if check_db_connection():
        sys.exit(0)
    else:
        sys.exit(1)