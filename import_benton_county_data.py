"""
Import script for Benton County, Washington property tax data.

This script processes the 2025 Benton County tax data and imports it into the
LevyMaster system database.
"""

import os
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import or_, and_
from flask import current_app

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

# Benton County specific constants
COUNTY_NAME = "Benton"
STATE_CODE = "WA"
YEAR = 2025

# Data file paths
DATA_DIR = "2025"
LEVY_WORKSHEETS_DIR = os.path.join(DATA_DIR, "Levy Limitations Worksheets")
PRELIMINARY_VALUES_DIR = os.path.join(DATA_DIR, "Preliminary Values 2025")
DOR_REPORTS_DIR = os.path.join(DATA_DIR, "DOR Reports")
CERTIFICATION_DIR = os.path.join(DATA_DIR, "Certification to Treasurer")

# Map of district types to their common prefixes or identifying terms
DISTRICT_TYPE_MAPPING = {
    "City": "city",
    "County": "county",
    "Fire": "fire",
    "School": "school",
    "Library": "library",
    "Hospital": "hospital",
    "Cemetery": "cemetery",
    "Port": "port",
    "Park": "park",
    "Water": "water",
    "Sewer": "sewer",
    "Mosquito": "mosquito",
    "Irrigation": "irrigation",
    "EMS": "ems",
    "Public Utility": "pud",
}

def get_admin_user():
    """Get the admin user for audit tracking."""
    user = User.query.filter_by(is_administrator=True).first()
    if not user:
        user = User.query.first()  # Fallback to any user
    return user


def create_import_log(filename, import_type, status, notes=None, user_id=None):
    """Create an import log entry."""
    import_log = ImportLog(
        file_name=filename,
        import_type=import_type,
        status=status,
        notes=notes,
        user_id=user_id,
        year=YEAR
    )
    db.session.add(import_log)
    db.session.commit()
    return import_log


def guess_district_type(district_name):
    """Guess the district type based on its name."""
    district_name = district_name.lower()
    
    for type_name, keyword in DISTRICT_TYPE_MAPPING.items():
        if keyword in district_name:
            return type_name
            
    return "Other"


def import_districts_from_worksheets():
    """Import tax districts from levy limitation worksheets."""
    logger.info("Importing tax districts from levy limitation worksheets")
    
    admin_user = get_admin_user()
    worksheet_files = [f for f in os.listdir(LEVY_WORKSHEETS_DIR) if f.endswith('.xlsx')]
    
    for file in worksheet_files:
        try:
            file_path = os.path.join(LEVY_WORKSHEETS_DIR, file)
            logger.info(f"Processing {file}")
            
            # Extract district name from filename (typically "City of X 2025.xlsx" or similar)
            district_name = file.replace("2025.xlsx", "").strip()
            district_name = district_name.replace(" - linked", "").replace(" - unlinked", "")
            
            # Guess district type from name
            district_type = guess_district_type(district_name)
            
            # Check if district already exists
            existing_district = TaxDistrict.query.filter(
                and_(
                    TaxDistrict.district_name == district_name,
                    TaxDistrict.county == COUNTY_NAME,
                    TaxDistrict.state == STATE_CODE,
                    TaxDistrict.year == YEAR
                )
            ).first()
            
            if existing_district:
                logger.info(f"District {district_name} already exists, skipping")
                continue
            
            # Try to read the worksheet to extract additional information
            try:
                df = pd.read_excel(file_path, sheet_name=0)
                
                # Extract district code if available (format varies by worksheet)
                district_code = None
                # Logic to extract district code from worksheet would go here
                # This is highly dependent on specific worksheet format
                
                if not district_code:
                    # Generate a simple district code if none found
                    district_code = district_name.replace(" ", "_").lower()[:16]
                    
            except Exception as e:
                logger.warning(f"Could not extract additional info from {file}: {str(e)}")
                district_code = district_name.replace(" ", "_").lower()[:16]
            
            # Create the district record
            district = TaxDistrict(
                district_name=district_name,
                district_code=district_code,
                district_type=district_type,
                county=COUNTY_NAME,
                state=STATE_CODE,
                is_active=True,
                year=YEAR,
                created_by_id=admin_user.id if admin_user else None
            )
            
            db.session.add(district)
            db.session.commit()
            
            logger.info(f"Created district: {district_name} ({district_code})")
            
            # Create import log
            create_import_log(
                filename=file,
                import_type=ImportType.TAX_DISTRICT,
                status="COMPLETED",
                notes=f"Imported district {district_name}",
                user_id=admin_user.id if admin_user else None
            )
            
        except Exception as e:
            logger.error(f"Error processing {file}: {str(e)}")
            db.session.rollback()
            
            # Log the error
            create_import_log(
                filename=file,
                import_type=ImportType.TAX_DISTRICT,
                status="FAILED",
                notes=f"Error: {str(e)}",
                user_id=admin_user.id if admin_user else None
            )
    
    logger.info("Completed importing tax districts")


def import_tax_codes_from_cert_report():
    """Import tax codes from certification report."""
    logger.info("Importing tax codes from certification report")
    
    admin_user = get_admin_user()
    
    try:
        # Look for the certification report file
        cert_files = [f for f in os.listdir(DOR_REPORTS_DIR) if "Certification of Levies" in f]
        
        if not cert_files:
            logger.warning("Certification of Levies report not found")
            return
            
        cert_file = cert_files[0]
        file_path = os.path.join(DOR_REPORTS_DIR, cert_file)
        
        # Create import log
        import_log = create_import_log(
            filename=cert_file,
            import_type=ImportType.TAX_CODE,
            status="PROCESSING",
            notes="Started processing tax codes",
            user_id=admin_user.id if admin_user else None
        )
        
        # Read the certification file
        df = pd.read_excel(file_path)
        
        # Process the data to extract tax codes
        # The actual column names and data format will depend on the specific file
        # Below is a simplified example assuming the file has columns for tax code and district
        
        # Count successful imports
        success_count = 0
        
        # Use existing districts from the database
        districts = TaxDistrict.query.filter_by(county=COUNTY_NAME, state=STATE_CODE, year=YEAR).all()
        district_map = {d.district_name: d for d in districts}
        
        # For each tax code in the file
        # This logic would need to be adapted to the specific format of the certification file
        for index, row in df.iterrows():
            try:
                # Example: extract tax code and district info from the row
                # This is a placeholder - actual column names will vary
                if 'Tax Code' in row and 'District' in row and 'Assessed Value' in row:
                    tax_code_val = str(row['Tax Code'])
                    district_name = row['District']
                    assessed_value = float(row['Assessed Value'])
                    
                    # Find the district
                    district = None
                    for name, dist in district_map.items():
                        if district_name in name or name in district_name:
                            district = dist
                            break
                    
                    if not district:
                        logger.warning(f"District not found for tax code {tax_code_val}")
                        continue
                    
                    # Check if tax code already exists
                    existing_code = TaxCode.query.filter(
                        and_(
                            TaxCode.tax_code == tax_code_val,
                            TaxCode.tax_district_id == district.id,
                            TaxCode.year == YEAR
                        )
                    ).first()
                    
                    if existing_code:
                        logger.info(f"Tax code {tax_code_val} already exists for district {district.district_name}")
                        continue
                    
                    # Create the tax code
                    tax_code = TaxCode(
                        tax_code=tax_code_val,
                        tax_district_id=district.id,
                        description=f"Tax code {tax_code_val} for {district.district_name}",
                        total_assessed_value=assessed_value,
                        year=YEAR,
                        created_by_id=admin_user.id if admin_user else None
                    )
                    
                    db.session.add(tax_code)
                    success_count += 1
                    
                    # Commit every 100 records to avoid large transactions
                    if success_count % 100 == 0:
                        db.session.commit()
                        logger.info(f"Committed {success_count} tax codes")
            
            except Exception as e:
                logger.warning(f"Error processing row {index}: {str(e)}")
        
        # Final commit
        db.session.commit()
        
        # Update import log
        import_log.status = "COMPLETED"
        import_log.notes = f"Successfully imported {success_count} tax codes"
        db.session.commit()
        
        logger.info(f"Completed importing {success_count} tax codes")
        
    except Exception as e:
        logger.error(f"Error importing tax codes: {str(e)}")
        db.session.rollback()
        
        # Update import log if it exists
        if 'import_log' in locals():
            import_log.status = "FAILED"
            import_log.notes = f"Error: {str(e)}"
            db.session.commit()


def import_levy_rates():
    """Import levy rates from levy reports."""
    logger.info("Importing levy rates")
    
    admin_user = get_admin_user()
    
    try:
        # Look for the levy report file
        levy_files = [f for f in os.listdir(DOR_REPORTS_DIR) if "LevyRpt" in f]
        
        if not levy_files:
            logger.warning("Levy report not found")
            return
            
        levy_file = levy_files[0]
        file_path = os.path.join(DOR_REPORTS_DIR, levy_file)
        
        # Create import log
        import_log = create_import_log(
            filename=levy_file,
            import_type=ImportType.RATE,
            status="PROCESSING",
            notes="Started processing levy rates",
            user_id=admin_user.id if admin_user else None
        )
        
        # Read the levy report file
        df = pd.read_excel(file_path)
        
        # Process the data to extract levy rates
        # The actual column names and data format will depend on the specific file
        # Below is a simplified example
        
        # Count successful imports
        success_count = 0
        
        # Get all tax codes for the county and year
        tax_codes = TaxCode.query.join(TaxDistrict).filter(
            and_(
                TaxDistrict.county == COUNTY_NAME,
                TaxDistrict.state == STATE_CODE,
                TaxCode.year == YEAR
            )
        ).all()
        
        # Create a map for quick lookup
        tax_code_map = {tc.tax_code: tc for tc in tax_codes}
        
        # For each levy rate in the file
        # This logic would need to be adapted to the specific format of the levy report
        for index, row in df.iterrows():
            try:
                # Example: extract tax code, levy rate, and levy amount from the row
                # This is a placeholder - actual column names will vary
                if 'Tax Code' in row and 'Levy Rate' in row and 'Levy Amount' in row:
                    tax_code_val = str(row['Tax Code'])
                    levy_rate = float(row['Levy Rate'])
                    levy_amount = float(row['Levy Amount'])
                    
                    # Find the tax code
                    if tax_code_val not in tax_code_map:
                        logger.warning(f"Tax code {tax_code_val} not found")
                        continue
                    
                    tax_code = tax_code_map[tax_code_val]
                    
                    # Check if historical rate already exists
                    existing_rate = TaxCodeHistoricalRate.query.filter(
                        and_(
                            TaxCodeHistoricalRate.tax_code_id == tax_code.id,
                            TaxCodeHistoricalRate.year == YEAR
                        )
                    ).first()
                    
                    if existing_rate:
                        logger.info(f"Historical rate already exists for tax code {tax_code_val}")
                        
                        # Update the existing rate
                        existing_rate.levy_rate = levy_rate
                        existing_rate.levy_amount = levy_amount
                        existing_rate.total_assessed_value = tax_code.total_assessed_value
                        existing_rate.updated_by_id = admin_user.id if admin_user else None
                    else:
                        # Create the historical rate
                        historical_rate = TaxCodeHistoricalRate(
                            tax_code_id=tax_code.id,
                            year=YEAR,
                            levy_rate=levy_rate,
                            levy_amount=levy_amount,
                            total_assessed_value=tax_code.total_assessed_value,
                            created_by_id=admin_user.id if admin_user else None
                        )
                        
                        db.session.add(historical_rate)
                    
                    # Also update the tax code record
                    tax_code.effective_tax_rate = levy_rate
                    tax_code.total_levy_amount = levy_amount
                    
                    success_count += 1
                    
                    # Commit every 100 records to avoid large transactions
                    if success_count % 100 == 0:
                        db.session.commit()
                        logger.info(f"Committed {success_count} levy rates")
            
            except Exception as e:
                logger.warning(f"Error processing row {index}: {str(e)}")
        
        # Final commit
        db.session.commit()
        
        # Update import log
        import_log.status = "COMPLETED"
        import_log.notes = f"Successfully imported {success_count} levy rates"
        db.session.commit()
        
        logger.info(f"Completed importing {success_count} levy rates")
        
    except Exception as e:
        logger.error(f"Error importing levy rates: {str(e)}")
        db.session.rollback()
        
        # Update import log if it exists
        if 'import_log' in locals():
            import_log.status = "FAILED"
            import_log.notes = f"Error: {str(e)}"
            db.session.commit()


def import_preliminary_values():
    """Import preliminary assessed values."""
    logger.info("Importing preliminary assessed values")
    
    admin_user = get_admin_user()
    
    # Find the most recent preliminary values spreadsheet
    # We'll use the "3rd Preliminary Values" if available since it's likely most up-to-date
    prelim_files = [f for f in os.listdir(PRELIMINARY_VALUES_DIR) 
                  if f.endswith('.xlsx') and '3rd Preliminary' in f]
    
    if not prelim_files:
        # Try 2nd preliminary
        prelim_files = [f for f in os.listdir(PRELIMINARY_VALUES_DIR) 
                      if f.endswith('.xlsx') and '2nd Preliminary' in f]
    
    if not prelim_files:
        # Try 1st preliminary
        prelim_files = [f for f in os.listdir(PRELIMINARY_VALUES_DIR) 
                      if f.endswith('.xlsx') and '1st Preliminary' in f]
    
    if not prelim_files:
        logger.warning("No preliminary values files found")
        return
    
    # Take the first matching file
    prelim_file = prelim_files[0]
    file_path = os.path.join(PRELIMINARY_VALUES_DIR, prelim_file)
    
    try:
        # Create import log
        import_log = create_import_log(
            filename=prelim_file,
            import_type=ImportType.PROPERTY,
            status="PROCESSING",
            notes="Started processing preliminary values",
            user_id=admin_user.id if admin_user else None
        )
        
        # Read the preliminary values file
        df = pd.read_excel(file_path)
        
        # Process the data to update tax code assessed values
        # This is highly dependent on the specific format of the preliminary values file
        
        # Count successful updates
        success_count = 0
        
        # Get existing tax codes for quick lookup
        tax_codes = TaxCode.query.join(TaxDistrict).filter(
            and_(
                TaxDistrict.county == COUNTY_NAME,
                TaxDistrict.state == STATE_CODE,
                TaxCode.year == YEAR
            )
        ).all()
        
        tax_code_map = {tc.tax_code: tc for tc in tax_codes}
        
        # For each row in the preliminary values file
        # This logic would need to be adapted to the specific format of the file
        for index, row in df.iterrows():
            try:
                # Example: extract tax code and assessed value from the row
                # This is a placeholder - actual column names will vary
                if 'Tax Code' in row and 'Assessed Value' in row:
                    tax_code_val = str(row['Tax Code'])
                    assessed_value = float(row['Assessed Value'])
                    
                    # Find the tax code
                    if tax_code_val not in tax_code_map:
                        logger.warning(f"Tax code {tax_code_val} not found")
                        continue
                    
                    tax_code = tax_code_map[tax_code_val]
                    
                    # Update the tax code's assessed value
                    tax_code.total_assessed_value = assessed_value
                    
                    # Also update the historical rate if it exists
                    historical_rate = TaxCodeHistoricalRate.query.filter(
                        and_(
                            TaxCodeHistoricalRate.tax_code_id == tax_code.id,
                            TaxCodeHistoricalRate.year == YEAR
                        )
                    ).first()
                    
                    if historical_rate:
                        historical_rate.total_assessed_value = assessed_value
                    
                    success_count += 1
                    
                    # Commit every 100 records to avoid large transactions
                    if success_count % 100 == 0:
                        db.session.commit()
                        logger.info(f"Committed {success_count} assessed value updates")
            
            except Exception as e:
                logger.warning(f"Error processing row {index}: {str(e)}")
        
        # Final commit
        db.session.commit()
        
        # Update import log
        import_log.status = "COMPLETED"
        import_log.notes = f"Successfully updated {success_count} assessed values"
        db.session.commit()
        
        logger.info(f"Completed importing {success_count} assessed values")
        
    except Exception as e:
        logger.error(f"Error importing preliminary values: {str(e)}")
        db.session.rollback()
        
        # Update import log if it exists
        if 'import_log' in locals():
            import_log.status = "FAILED"
            import_log.notes = f"Error: {str(e)}"
            db.session.commit()


def main():
    """Main import function."""
    logger.info("Starting Benton County data import")
    
    # Create a Flask application context for database operations
    app = create_app()
    
    with app.app_context():
        # Step 1: Import tax districts from levy worksheets
        import_districts_from_worksheets()
        
        # Step 2: Import tax codes from certification report
        import_tax_codes_from_cert_report()
        
        # Step 3: Import levy rates
        import_levy_rates()
        
        # Step 4: Import preliminary assessed values
        import_preliminary_values()
    
    logger.info("Completed Benton County data import")


if __name__ == "__main__":
    main()