"""
Migration script to fix historical analysis issues with AuditMixin columns.

This script updates the utils/advanced_historical_analysis.py file to use
explicit column selection that's compatible with the database schema, avoiding
queries for columns that don't exist.
"""

import os
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """
    Fix historical analysis by replacing the file with a fixed version.
    """
    original_file = 'utils/advanced_historical_analysis.py'
    fixed_file = 'utils/advanced_historical_analysis_fixed.py'
    backup_file = 'utils/advanced_historical_analysis.py.bak'
    
    try:
        # Ensure the fixed file exists
        if not os.path.exists(fixed_file):
            logger.error(f"Fixed file {fixed_file} does not exist")
            return False
        
        # Create a backup of the original file
        if os.path.exists(original_file):
            logger.info(f"Creating backup of {original_file} to {backup_file}")
            shutil.copy2(original_file, backup_file)
        
        # Replace the original file with the fixed version
        logger.info(f"Replacing {original_file} with {fixed_file}")
        shutil.copy2(fixed_file, original_file)
        
        logger.info("Historical analysis fixed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False

if __name__ == "__main__":
    logger.info("Running migration to fix historical analysis...")
    success = run_migration()
    
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
        exit(1)