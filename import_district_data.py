"""
Import district data from CSV into the TerraFusion database.

This script imports tax district data from CSV files into the existing database,
matching the actual database schema structure.
"""

import os
import csv
import logging
import psycopg2
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
COUNTY_NAME = "Benton"
STATE_CODE = "WA"
YEAR = 2025

# Data file paths
DATA_DIR = "2025"
TAX_DISTRICTS_FILE = os.path.join(DATA_DIR, "sample_tax_districts.csv")

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

def get_admin_user():
    """Get the admin user ID for audit tracking."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Try to get an admin user (using is_admin, not is_administrator)
        cursor.execute(
            "SELECT id FROM \"user\" WHERE is_admin = TRUE LIMIT 1"
        )
        
        user = cursor.fetchone()
        if user:
            return user[0]
        
        # If no admin user, get any user
        cursor.execute("SELECT id FROM \"user\" LIMIT 1")
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return user[0] if user else None
    
    except Exception as e:
        logger.error(f"Error getting admin user: {str(e)}")
        if conn:
            conn.close()
        return None

def create_import_log(filename, import_type, status, notes=None, user_id=None):
    """Create an import log entry."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Create import log entry - using correct column names from the schema
        now = datetime.utcnow()
        cursor.execute(
            """
            INSERT INTO import_log (
                filename, import_type, status, notes, user_id, year, 
                import_date, records_imported, records_skipped
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                filename, import_type, status, notes, user_id, YEAR, 
                now, 0, 0
            )
        )
        
        import_log_id = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Created import log entry with ID {import_log_id}")
        return import_log_id
    
    except Exception as e:
        logger.error(f"Error creating import log: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return None

def update_import_log(log_id, status, notes, records_imported=0, records_skipped=0):
    """Update an existing import log entry."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Update import log
        cursor.execute(
            """
            UPDATE import_log 
            SET status = %s, notes = %s, records_imported = %s, records_skipped = %s
            WHERE id = %s
            """,
            (status, notes, records_imported, records_skipped, log_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Updated import log ID {log_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating import log: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def import_tax_districts():
    """Import tax districts from CSV file."""
    logger.info("Importing tax districts from CSV")
    
    admin_user_id = get_admin_user()
    
    if not os.path.exists(TAX_DISTRICTS_FILE):
        logger.error(f"Tax districts file {TAX_DISTRICTS_FILE} not found")
        return 0
    
    # Create import log
    import_log_id = create_import_log(
        filename=TAX_DISTRICTS_FILE,
        import_type="TAX_DISTRICT",
        status="PROCESSING",
        notes="Started processing tax districts from CSV",
        user_id=admin_user_id
    )
    
    if not import_log_id:
        logger.error("Failed to create import log, aborting import")
        return 0
    
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database, aborting import")
        update_import_log(
            import_log_id, 
            "FAILED", 
            "Database connection failed"
        )
        return 0
    
    try:
        cursor = conn.cursor()
        
        # Read the CSV file
        success_count = 0
        skip_count = 0
        
        with open(TAX_DISTRICTS_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    district_name = row.get('Tax District', '')
                    district_type = row.get('District Type', '')
                    county = row.get('County', COUNTY_NAME)
                    state = row.get('State', STATE_CODE)
                    
                    # Skip empty rows
                    if not district_name:
                        skip_count += 1
                        continue
                    
                    # Check if district already exists
                    cursor.execute(
                        """
                        SELECT id FROM tax_district 
                        WHERE district_name = %s AND county = %s AND state = %s AND year = %s
                        """,
                        (district_name, county, state, YEAR)
                    )
                    
                    existing_district = cursor.fetchone()
                    
                    if existing_district:
                        logger.info(f"District {district_name} already exists, skipping")
                        skip_count += 1
                        continue
                    
                    # Create district code from name
                    district_code = district_name.replace(" ", "_").lower()[:16]
                    
                    # Create the district record
                    now = datetime.utcnow()
                    cursor.execute(
                        """
                        INSERT INTO tax_district (
                            district_name, district_code, district_type, county, state,
                            is_active, year, created_by_id, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (
                            district_name, district_code, district_type, county, state,
                            True, YEAR, admin_user_id, now, now
                        )
                    )
                    
                    district_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    logger.info(f"Created district: {district_name} ({district_code}) with ID {district_id}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing district {row.get('Tax District', 'unknown')}: {str(e)}")
                    conn.rollback()
        
        # Update import log
        update_import_log(
            import_log_id,
            "COMPLETED", 
            f"Successfully imported {success_count} tax districts, skipped {skip_count}",
            success_count,
            skip_count
        )
        
        cursor.close()
        conn.close()
        
        logger.info(f"Completed importing {success_count} tax districts, skipped {skip_count}")
        return success_count
    
    except Exception as e:
        logger.error(f"Error importing tax districts: {str(e)}")
        
        if conn:
            conn.close()
        
        # Update import log with error
        update_import_log(
            import_log_id,
            "FAILED", 
            f"Error importing tax districts: {str(e)}"
        )
        
        return 0

def main():
    """Main import function."""
    logger.info("Starting tax district data import")
    
    # Import tax districts
    districts_imported = import_tax_districts()
    logger.info(f"Imported {districts_imported} tax districts")
    
    logger.info("Completed tax district data import")

if __name__ == "__main__":
    main()