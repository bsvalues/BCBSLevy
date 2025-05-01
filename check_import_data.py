"""
Admin tool to check database contents after import.

This script connects to the database and displays summary statistics
of imported data for verification and troubleshooting.
"""

import os
import logging
from sqlalchemy import func

from app import db, create_app
from models import (
    TaxDistrict,
    TaxCode,
    TaxCodeHistoricalRate,
    Property,
    ImportLog,
    ImportType,
    User
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_tax_districts():
    """Check imported tax districts."""
    count = TaxDistrict.query.count()
    logger.info(f"Total tax districts: {count}")
    
    # Show sample districts
    districts = TaxDistrict.query.limit(5).all()
    logger.info("Sample tax districts:")
    for district in districts:
        logger.info(f"  - {district.district_name} ({district.district_code}): {district.district_type}, {district.county}, {district.state}, {district.year}")
    
    # Show counts by district type
    district_types = db.session.query(
        TaxDistrict.district_type, 
        func.count(TaxDistrict.id)
    ).group_by(TaxDistrict.district_type).all()
    
    logger.info("District counts by type:")
    for district_type, count in district_types:
        logger.info(f"  - {district_type}: {count}")
    
    return count

def check_tax_codes():
    """Check imported tax codes."""
    count = TaxCode.query.count()
    logger.info(f"Total tax codes: {count}")
    
    # Show sample tax codes
    tax_codes = TaxCode.query.limit(5).all()
    logger.info("Sample tax codes:")
    for tax_code in tax_codes:
        district_name = tax_code.tax_district.district_name if tax_code.tax_district else "Unknown"
        logger.info(f"  - {tax_code.tax_code}: District: {district_name}, AV: ${tax_code.total_assessed_value:,.2f}, Levy: ${tax_code.total_levy_amount:,.2f}, Rate: {tax_code.effective_tax_rate:.6f}")
    
    # Show counts by district
    district_counts = db.session.query(
        TaxDistrict.district_name, 
        func.count(TaxCode.id)
    ).join(TaxCode).group_by(TaxDistrict.district_name).all()
    
    logger.info("Tax code counts by district:")
    for district_name, count in district_counts:
        logger.info(f"  - {district_name}: {count}")
    
    return count

def check_historical_rates():
    """Check imported historical rates."""
    count = TaxCodeHistoricalRate.query.count()
    logger.info(f"Total historical rates: {count}")
    
    # Show sample historical rates
    rates = TaxCodeHistoricalRate.query.limit(5).all()
    logger.info("Sample historical rates:")
    for rate in rates:
        tax_code = TaxCode.query.get(rate.tax_code_id)
        tax_code_number = tax_code.tax_code if tax_code else "Unknown"
        district_name = tax_code.tax_district.district_name if tax_code and tax_code.tax_district else "Unknown"
        
        logger.info(f"  - Tax Code: {tax_code_number}, District: {district_name}, Year: {rate.year}, Rate: {rate.levy_rate:.6f}, AV: ${rate.total_assessed_value:,.2f}, Levy: ${rate.levy_amount:,.2f}")
    
    # Show counts by year
    year_counts = db.session.query(
        TaxCodeHistoricalRate.year, 
        func.count(TaxCodeHistoricalRate.id)
    ).group_by(TaxCodeHistoricalRate.year).all()
    
    logger.info("Historical rate counts by year:")
    for year, count in year_counts:
        logger.info(f"  - {year}: {count}")
    
    return count

def check_properties():
    """Check imported properties."""
    count = Property.query.count()
    logger.info(f"Total properties: {count}")
    
    # Show sample properties
    properties = Property.query.limit(5).all()
    logger.info("Sample properties:")
    for prop in properties:
        tax_code = TaxCode.query.get(prop.tax_code_id)
        tax_code_number = tax_code.tax_code if tax_code else "Unknown"
        district_name = tax_code.tax_district.district_name if tax_code and tax_code.tax_district else "Unknown"
        
        logger.info(f"  - Parcel: {prop.parcel_id}, Tax Code: {tax_code_number}, District: {district_name}, Type: {prop.property_type.name}, AV: ${prop.assessed_value:,.2f}")
    
    # Show counts by property type
    type_counts = db.session.query(
        Property.property_type, 
        func.count(Property.id)
    ).group_by(Property.property_type).all()
    
    logger.info("Property counts by type:")
    for prop_type, count in type_counts:
        logger.info(f"  - {prop_type.name}: {count}")
    
    return count

def check_import_logs():
    """Check import logs."""
    count = ImportLog.query.count()
    logger.info(f"Total import logs: {count}")
    
    # Show recent import logs
    logs = ImportLog.query.order_by(ImportLog.id.desc()).limit(10).all()
    logger.info("Recent import logs:")
    for log in logs:
        user = User.query.get(log.user_id)
        username = user.username if user else "Unknown"
        
        logger.info(f"  - {log.file_name}: Type: {log.import_type.name}, Status: {log.status}, User: {username}, Date: {log.created_at}")
    
    # Show counts by status
    status_counts = db.session.query(
        ImportLog.status, 
        func.count(ImportLog.id)
    ).group_by(ImportLog.status).all()
    
    logger.info("Import log counts by status:")
    for status, count in status_counts:
        logger.info(f"  - {status}: {count}")
    
    return count

def main():
    """Main function to check database contents."""
    logger.info("Starting database content check")
    
    # Create a Flask application context for database operations
    app = create_app()
    
    with app.app_context():
        # Check each data type
        district_count = check_tax_districts()
        tax_code_count = check_tax_codes()
        rate_count = check_historical_rates()
        property_count = check_properties()
        log_count = check_import_logs()
        
        # Summary
        logger.info("Database content summary:")
        logger.info(f"  - Tax Districts: {district_count}")
        logger.info(f"  - Tax Codes: {tax_code_count}")
        logger.info(f"  - Historical Rates: {rate_count}")
        logger.info(f"  - Properties: {property_count}")
        logger.info(f"  - Import Logs: {log_count}")
    
    logger.info("Database content check complete")

if __name__ == "__main__":
    main()