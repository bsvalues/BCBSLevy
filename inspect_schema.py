"""
Inspect the database schema to understand table structure.

This script inspects key tables in the database to understand their structure
for proper data import.
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

def inspect_table_columns(table_name):
    """Inspect the columns of a specific table."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get column information for the table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        logger.info(f"Structure of table '{table_name}':")
        logger.info("-" * 80)
        logger.info(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10} {'Default':<20}")
        logger.info("-" * 80)
        
        for column in columns:
            col_name, data_type, is_nullable, default = column
            logger.info(f"{col_name:<30} {data_type:<20} {is_nullable:<10} {str(default)[:20] if default else ''}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error inspecting table {table_name}: {str(e)}")
        if conn:
            conn.close()

def main():
    """Main function to inspect the database schema."""
    # Tables we want to inspect
    tables_to_inspect = [
        "user", "import_log", "tax_district", "tax_code", "tax_code_historical_rate"
    ]
    
    # Inspect each table
    for table in tables_to_inspect:
        inspect_table_columns(table)
        logger.info("\n")

if __name__ == "__main__":
    main()