"""
Check tax district data in the database.

This script checks the tax districts imported into the database.
"""

import os
import logging
import psycopg2
from prettytable import PrettyTable

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the database."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not found")
        return None
    
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def check_tax_districts():
    """Check tax districts in the database."""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all tax districts
        cursor.execute(
            """
            SELECT id, district_name, district_code, district_type, year, county, state
            FROM tax_district
            ORDER BY district_name
            """
        )
        
        districts = cursor.fetchall()
        
        # Print results as a table
        table = PrettyTable()
        table.field_names = ["ID", "District Name", "District Code", "Type", "Year", "County", "State"]
        
        for district in districts:
            table.add_row(district)
        
        print(table)
        logger.info(f"Found {len(districts)} tax districts in the database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking tax districts: {str(e)}")
        if conn:
            conn.close()

def check_import_logs():
    """Check import logs in the database."""
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Get all import logs
        cursor.execute(
            """
            SELECT id, filename, import_type, status, import_date, records_imported, records_skipped
            FROM import_log
            ORDER BY import_date DESC
            """
        )
        
        logs = cursor.fetchall()
        
        # Print results as a table
        table = PrettyTable()
        table.field_names = ["ID", "Filename", "Type", "Status", "Date", "Imported", "Skipped"]
        
        for log in logs:
            table.add_row(log)
        
        print(table)
        logger.info(f"Found {len(logs)} import logs in the database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking import logs: {str(e)}")
        if conn:
            conn.close()

def main():
    """Main function to check database data."""
    logger.info("Checking database data")
    
    # Check data
    check_tax_districts()
    check_import_logs()
    
    logger.info("Database check completed")

if __name__ == "__main__":
    main()