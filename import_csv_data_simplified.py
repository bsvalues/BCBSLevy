"""
Simplified import script for TerraFusion data in CSV format.

This script is designed to work with CSV data files,
making it easier to test and validate the import process.
"""

import os
import csv
import logging
from datetime import datetime

from app import db, create_app
from models import (
    TaxDistrict,
    TaxCode,
    TaxCodeHistoricalRate,
    Property,
    ImportLog,
    ImportType,
    PropertyType,
    User
)

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

def get_admin_user():
    """Get the admin user for audit tracking."""
    user = User.query.filter_by(is_administrator=True).first()
    if not user:
        user = User.query.first()  # Fallback to any user
    return user

def create_import_log(filename, import_type, status, notes=None, user_id=None):
    """Create an import log entry."""
    import_log = ImportLog()
    import_log.file_name = filename
    import_log.import_type = import_type
    import_log.status = status
    import_log.notes = notes
    import_log.user_id = user_id
    import_log.year = YEAR
    
    db.session.add(import_log)
    db.session.commit()
    return import_log

def import_tax_districts():
    """Import tax districts from CSV file."""
    logger.info("Importing tax districts from CSV")
    
    admin_user = get_admin_user()
    
    if not os.path.exists(TAX_DISTRICTS_FILE):
        logger.error(f"Tax districts file {TAX_DISTRICTS_FILE} not found")
        return 0
    
    # Create import log
    import_log = create_import_log(
        filename=TAX_DISTRICTS_FILE,
        import_type=ImportType.TAX_DISTRICT,
        status="PROCESSING",
        notes="Started processing tax districts from CSV",
        user_id=admin_user.id if admin_user else None
    )
    
    try:
        # Read the CSV file using standard csv module
        success_count = 0
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
                        continue
                    
                    # Check if district already exists
                    existing_district = TaxDistrict.query.filter_by(
                        district_name=district_name,
                        county=county,
                        state=state,
                        year=YEAR
                    ).first()
                    
                    if existing_district:
                        logger.info(f"District {district_name} already exists, skipping")
                        continue
                    
                    # Create district code from name
                    district_code = district_name.replace(" ", "_").lower()[:16]
                    
                    # Create the district record
                    district = TaxDistrict()
                    district.district_name = district_name
                    district.district_code = district_code
                    district.district_type = district_type
                    district.county = county
                    district.state = state
                    district.is_active = True
                    district.year = YEAR
                    district.created_by_id = admin_user.id if admin_user else None
                    
                    db.session.add(district)
                    db.session.commit()
                    
                    logger.info(f"Created district: {district_name} ({district_code})")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing district {row.get('Tax District', 'unknown')}: {str(e)}")
                    db.session.rollback()
        
        # Update import log
        import_log.status = "COMPLETED"
        import_log.notes = f"Successfully imported {success_count} tax districts"
        db.session.commit()
        
        logger.info(f"Completed importing {success_count} tax districts")
        return success_count
    
    except Exception as e:
        logger.error(f"Error importing tax districts: {str(e)}")
        import_log.status = "FAILED"
        import_log.notes = f"Error importing tax districts: {str(e)}"
        db.session.commit()
        return 0

def main():
    """Main import function."""
    logger.info("Starting CSV data import")
    
    # Create a Flask application context for database operations
    app = create_app()
    
    with app.app_context():
        # Step 1: Import tax districts
        districts_imported = import_tax_districts()
        logger.info(f"Imported {districts_imported} tax districts")
    
    logger.info("Completed CSV data import")

if __name__ == "__main__":
    main()