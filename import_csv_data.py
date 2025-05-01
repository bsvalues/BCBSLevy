"""
Simplified import script for TerraFusion data in CSV format.

This script is designed to work with CSV data files rather than Excel files,
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
TAX_CODES_FILE = os.path.join(DATA_DIR, "sample_tax_codes.csv")
LEVY_RATES_FILE = os.path.join(DATA_DIR, "sample_levy_rates.csv")
PROPERTY_VALUES_FILE = os.path.join(DATA_DIR, "sample_property_values.csv")

def get_admin_user():
    """Get the admin user for audit tracking."""
    user = User.query.filter_by(is_administrator=True).first()
    if not user:
        user = User.query.first()  # Fallback to any user
    if not user:
        # Create a default admin user if none exists
        logger.info("Creating default admin user")
        user = User(
            username="admin",
            email="admin@terralevymaster.com",
            password_hash="$2b$12$JE7tOMTakIvFgBNXJ04J5OQgLYYRsIk7jIinZ8ZYNQ0zTZxSQjtFW",  # Password: admin
            first_name="Admin",
            last_name="User",
            is_active=True,
            is_administrator=True
        )
        db.session.add(user)
        db.session.commit()
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

def import_tax_districts():
    """Import tax districts from CSV file."""
    logger.info("Importing tax districts from CSV")
    
    admin_user = get_admin_user()
    
    if not os.path.exists(TAX_DISTRICTS_FILE):
        logger.error(f"Tax districts file {TAX_DISTRICTS_FILE} not found")
        return
    
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
                    district = TaxDistrict(
                        district_name=district_name,
                        district_code=district_code,
                        district_type=district_type,
                        county=county,
                        state=state,
                        is_active=True,
                        year=YEAR,
                        created_by_id=admin_user.id if admin_user else None
                    )
                    
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

def import_tax_codes():
    """Import tax codes from CSV file."""
    logger.info("Importing tax codes from CSV")
    
    admin_user = get_admin_user()
    
    if not os.path.exists(TAX_CODES_FILE):
        logger.error(f"Tax codes file {TAX_CODES_FILE} not found")
        return
    
    # Create import log
    import_log = create_import_log(
        filename=TAX_CODES_FILE,
        import_type=ImportType.TAX_CODE,
        status="PROCESSING",
        notes="Started processing tax codes from CSV",
        user_id=admin_user.id if admin_user else None
    )
    
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(TAX_CODES_FILE)
        
        success_count = 0
        for idx, row in df.iterrows():
            try:
                tax_code = row.get('Tax Code', '')
                district_name = row.get('Tax District', '')
                description = row.get('Description', '')
                total_assessed_value = float(row.get('Assessed Value', 0))
                total_levy_amount = float(row.get('Levy Amount', 0))
                effective_tax_rate = float(row.get('Tax Rate', 0))
                
                # Skip empty rows
                if not tax_code or not district_name:
                    continue
                
                # Find the district
                district = TaxDistrict.query.filter(
                    and_(
                        TaxDistrict.district_name == district_name,
                        TaxDistrict.county == COUNTY_NAME,
                        TaxDistrict.state == STATE_CODE,
                        TaxDistrict.year == YEAR
                    )
                ).first()
                
                if not district:
                    logger.warning(f"District {district_name} not found, skipping tax code {tax_code}")
                    continue
                
                # Check if tax code already exists
                existing_tax_code = TaxCode.query.filter(
                    and_(
                        TaxCode.tax_code == tax_code,
                        TaxCode.tax_district_id == district.id,
                        TaxCode.year == YEAR
                    )
                ).first()
                
                if existing_tax_code:
                    logger.info(f"Tax code {tax_code} already exists, updating")
                    existing_tax_code.description = description
                    existing_tax_code.total_assessed_value = total_assessed_value
                    existing_tax_code.total_levy_amount = total_levy_amount
                    existing_tax_code.effective_tax_rate = effective_tax_rate
                    existing_tax_code.updated_by_id = admin_user.id if admin_user else None
                    db.session.commit()
                    success_count += 1
                    continue
                
                # Create the tax code record
                new_tax_code = TaxCode(
                    tax_code=tax_code,
                    tax_district_id=district.id,
                    description=description,
                    total_assessed_value=total_assessed_value,
                    total_levy_amount=total_levy_amount,
                    effective_tax_rate=effective_tax_rate,
                    year=YEAR,
                    created_by_id=admin_user.id if admin_user else None
                )
                
                db.session.add(new_tax_code)
                db.session.commit()
                
                logger.info(f"Created tax code: {tax_code} for district {district_name}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing tax code {row.get('Tax Code', 'unknown')}: {str(e)}")
                db.session.rollback()
        
        # Update import log
        import_log.status = "COMPLETED"
        import_log.notes = f"Successfully imported {success_count} tax codes"
        db.session.commit()
        
        logger.info(f"Completed importing {success_count} tax codes")
        return success_count
    
    except Exception as e:
        logger.error(f"Error importing tax codes: {str(e)}")
        import_log.status = "FAILED"
        import_log.notes = f"Error importing tax codes: {str(e)}"
        db.session.commit()
        return 0

def import_levy_rates():
    """Import levy rates from CSV file."""
    logger.info("Importing levy rates from CSV")
    
    admin_user = get_admin_user()
    
    if not os.path.exists(LEVY_RATES_FILE):
        logger.error(f"Levy rates file {LEVY_RATES_FILE} not found")
        return
    
    # Create import log
    import_log = create_import_log(
        filename=LEVY_RATES_FILE,
        import_type=ImportType.RATE,
        status="PROCESSING",
        notes="Started processing levy rates from CSV",
        user_id=admin_user.id if admin_user else None
    )
    
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(LEVY_RATES_FILE)
        
        success_count = 0
        for idx, row in df.iterrows():
            try:
                tax_code_id = row.get('Tax Code ID', '')
                year = int(row.get('Year', YEAR))
                levy_rate = float(row.get('Levy Rate', 0))
                levy_amount = float(row.get('Levy Amount', 0))
                total_assessed_value = float(row.get('Assessed Value', 0))
                
                # Skip empty rows
                if not tax_code_id:
                    continue
                
                # Find the tax code
                tax_code = TaxCode.query.get(tax_code_id)
                
                if not tax_code:
                    logger.warning(f"Tax code with ID {tax_code_id} not found, skipping")
                    continue
                
                # Check if historical rate already exists
                existing_rate = TaxCodeHistoricalRate.query.filter_by(
                    tax_code_id=tax_code_id,
                    year=year
                ).first()
                
                if existing_rate:
                    logger.info(f"Rate for tax code ID {tax_code_id} year {year} already exists, updating")
                    existing_rate.levy_rate = levy_rate
                    existing_rate.levy_amount = levy_amount
                    existing_rate.total_assessed_value = total_assessed_value
                    existing_rate.updated_at = datetime.utcnow()
                    db.session.commit()
                    success_count += 1
                    continue
                
                # Create the historical rate record
                new_rate = TaxCodeHistoricalRate(
                    tax_code_id=tax_code_id,
                    year=year,
                    levy_rate=levy_rate,
                    levy_amount=levy_amount,
                    total_assessed_value=total_assessed_value
                )
                
                db.session.add(new_rate)
                db.session.commit()
                
                logger.info(f"Created historical rate for tax code ID {tax_code_id} year {year}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing rate for tax code ID {row.get('Tax Code ID', 'unknown')}: {str(e)}")
                db.session.rollback()
        
        # Update import log
        import_log.status = "COMPLETED"
        import_log.notes = f"Successfully imported {success_count} levy rates"
        db.session.commit()
        
        logger.info(f"Completed importing {success_count} levy rates")
        return success_count
    
    except Exception as e:
        logger.error(f"Error importing levy rates: {str(e)}")
        import_log.status = "FAILED"
        import_log.notes = f"Error importing levy rates: {str(e)}"
        db.session.commit()
        return 0

def import_property_values():
    """Import property values from CSV file."""
    logger.info("Importing property values from CSV")
    
    admin_user = get_admin_user()
    
    if not os.path.exists(PROPERTY_VALUES_FILE):
        logger.error(f"Property values file {PROPERTY_VALUES_FILE} not found")
        return
    
    # Create import log
    import_log = create_import_log(
        filename=PROPERTY_VALUES_FILE,
        import_type=ImportType.PROPERTY,
        status="PROCESSING",
        notes="Started processing property values from CSV",
        user_id=admin_user.id if admin_user else None
    )
    
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(PROPERTY_VALUES_FILE)
        
        success_count = 0
        for idx, row in df.iterrows():
            try:
                parcel_id = row.get('Parcel ID', '')
                tax_code_id = row.get('Tax Code ID', '')
                property_type = row.get('Property Type', 'RESIDENTIAL')
                address = row.get('Address', '')
                city = row.get('City', '')
                zip_code = row.get('Zip Code', '')
                assessed_value = float(row.get('Assessed Value', 0))
                year = int(row.get('Year', YEAR))
                
                # Skip empty rows
                if not parcel_id or not tax_code_id:
                    continue
                
                # Find the tax code
                tax_code = TaxCode.query.get(tax_code_id)
                
                if not tax_code:
                    logger.warning(f"Tax code with ID {tax_code_id} not found, skipping property {parcel_id}")
                    continue
                
                # Convert property type string to enum
                try:
                    prop_type_enum = PropertyType[property_type.upper()]
                except (KeyError, AttributeError):
                    logger.warning(f"Invalid property type {property_type} for property {parcel_id}, using RESIDENTIAL")
                    prop_type_enum = PropertyType.RESIDENTIAL
                
                # Check if property already exists
                existing_property = Property.query.filter_by(
                    parcel_id=parcel_id,
                    year=year
                ).first()
                
                if existing_property:
                    logger.info(f"Property {parcel_id} year {year} already exists, updating")
                    existing_property.tax_code_id = tax_code_id
                    existing_property.property_type = prop_type_enum
                    existing_property.address = address
                    existing_property.city = city
                    existing_property.zip_code = zip_code
                    existing_property.assessed_value = assessed_value
                    existing_property.updated_by_id = admin_user.id if admin_user else None
                    db.session.commit()
                    success_count += 1
                    continue
                
                # Create the property record
                new_property = Property(
                    parcel_id=parcel_id,
                    tax_code_id=tax_code_id,
                    property_type=prop_type_enum,
                    address=address,
                    city=city,
                    zip_code=zip_code,
                    assessed_value=assessed_value,
                    year=year,
                    created_by_id=admin_user.id if admin_user else None
                )
                
                db.session.add(new_property)
                db.session.commit()
                
                logger.info(f"Created property record for parcel {parcel_id}")
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing property {row.get('Parcel ID', 'unknown')}: {str(e)}")
                db.session.rollback()
        
        # Update import log
        import_log.status = "COMPLETED"
        import_log.notes = f"Successfully imported {success_count} properties"
        db.session.commit()
        
        logger.info(f"Completed importing {success_count} properties")
        return success_count
    
    except Exception as e:
        logger.error(f"Error importing properties: {str(e)}")
        import_log.status = "FAILED"
        import_log.notes = f"Error importing properties: {str(e)}"
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
        
        # Step 2: Import tax codes
        if os.path.exists(TAX_CODES_FILE):
            tax_codes_imported = import_tax_codes()
            logger.info(f"Imported {tax_codes_imported} tax codes")
        else:
            logger.warning(f"Tax codes file {TAX_CODES_FILE} not found, skipping")
        
        # Step 3: Import levy rates
        if os.path.exists(LEVY_RATES_FILE):
            rates_imported = import_levy_rates()
            logger.info(f"Imported {rates_imported} levy rates")
        else:
            logger.warning(f"Levy rates file {LEVY_RATES_FILE} not found, skipping")
        
        # Step 4: Import property values
        if os.path.exists(PROPERTY_VALUES_FILE):
            properties_imported = import_property_values()
            logger.info(f"Imported {properties_imported} properties")
        else:
            logger.warning(f"Property values file {PROPERTY_VALUES_FILE} not found, skipping")
    
    logger.info("Completed CSV data import")

if __name__ == "__main__":
    main()