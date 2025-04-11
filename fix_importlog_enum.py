"""
Migration script to fix ImportLog records with invalid import_type values.

This script updates ImportLog records that have import_type values that don't match 
the currently defined enum values in the ImportType enum.
"""

import logging
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """
    Update ImportLog records with invalid import_type values.
    """
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        # Create engine
        engine = create_engine(database_url)
        
        # Connect to database
        with engine.connect() as connection:
            # Start transaction
            with connection.begin():
                # First, identify if there are any invalid values
                result = connection.execute(text(
                    "SELECT DISTINCT import_type FROM import_log WHERE import_type NOT IN ('TAX_DISTRICT', 'TAX_CODE', 'PROPERTY', 'RATE', 'LEVY', 'OTHER')"
                ))
                
                invalid_values = [row[0] for row in result if row[0]]
                logger.info(f"Found {len(invalid_values)} invalid import_type values: {invalid_values}")
                
                # Fix each invalid value
                for invalid_value in invalid_values:
                    # Determine what to map this value to
                    # For 'property', map to 'PROPERTY'
                    if invalid_value.lower() == 'property':
                        new_value = 'PROPERTY'
                    else:
                        new_value = 'OTHER'  # Default to OTHER for any other invalid values
                    
                    # Update records with this invalid value
                    connection.execute(text(
                        f"UPDATE import_log SET import_type = '{new_value}' WHERE import_type = '{invalid_value}'"
                    ))
                    
                    logger.info(f"Updated import_type from '{invalid_value}' to '{new_value}'")
            
            logger.info("Migration completed successfully")
            return True
                
    except Exception as e:
        logger.error(f"Error in migration: {str(e)}")
        return False

if __name__ == "__main__":
    run_migration()