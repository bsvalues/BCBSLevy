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
    
    # Also import districts from our other source files
    # 1. From the 5.90 file (contains district names and levy rates)
    try:
        file_path = os.path.join(DATA_DIR, "5.90.xlsx")
        if os.path.exists(file_path):
            df_590 = pd.read_excel(file_path)
            districts_590 = []
            
            # The district names are in the second column (Unnamed: 1) 
            # with a header row containing "Tax District"
            tax_district_col = None
            for col in df_590.columns:
                col_values = df_590[col].astype(str).str.lower()
                if col_values.str.contains('tax district').any():
                    tax_district_col = col
                    break
            
            if tax_district_col:
                # Find the row with "Tax District" text
                header_idx = df_590.index[df_590[tax_district_col].astype(str).str.lower() == 'tax district'][0]
                
                # Extract districts, skipping empty rows
                for idx, row in df_590.iloc[header_idx+1:].iterrows():
                    district_name = row[tax_district_col]
                    if pd.notna(district_name) and isinstance(district_name, str) and len(district_name.strip()) > 0:
                        districts_590.append(district_name.strip())
        
            logger.info(f"Found {len(districts_590)} districts in 5.90 file")
    except Exception as e:
        logger.error(f"Error reading 5.90 file: {str(e)}")
        districts_590 = []
    
    # 2. From the Constitutional 1% file (contains district names and rates)
    try:
        file_path = os.path.join(DATA_DIR, "2025 Constitutional 1%.xlsx")
        if os.path.exists(file_path):
            df_const = pd.read_excel(file_path)
            districts_const = []
            
            # The district names are in the second column (Unnamed: 1) 
            # with a header row containing "Tax District"
            tax_district_col = None
            for col in df_const.columns:
                col_values = df_const[col].astype(str).str.lower()
                if col_values.str.contains('tax district').any():
                    tax_district_col = col
                    break
            
            if tax_district_col:
                # Find the row with "Tax District" text
                header_idx = df_const.index[df_const[tax_district_col].astype(str).str.lower() == 'tax district'][0]
                
                # Extract districts, skipping empty rows
                for idx, row in df_const.iloc[header_idx+1:].iterrows():
                    district_name = row[tax_district_col]
                    if pd.notna(district_name) and isinstance(district_name, str) and len(district_name.strip()) > 0:
                        districts_const.append(district_name.strip())
        
            logger.info(f"Found {len(districts_const)} districts in Constitutional 1% file")
    except Exception as e:
        logger.error(f"Error reading Constitutional 1% file: {str(e)}")
        districts_const = []
    
    # 3. From County rate spread file
    try:
        file_path = os.path.join(DATA_DIR, "County rate spread 2025.xls")
        if os.path.exists(file_path):
            df_spread = pd.read_excel(file_path)
            districts_spread = []
            
            # In this file the district names are typically in the first column
            # We'll extract any non-empty value that doesn't look like a header
            for idx, row in df_spread.iterrows():
                col_val = row.iloc[0]  # First column
                if pd.notna(col_val) and isinstance(col_val, str) and len(col_val.strip()) > 0:
                    if not any(keyword in col_val.lower() for keyword in ['total', 'unnamed', 'line', 'rate']):
                        districts_spread.append(col_val.strip())
            
            logger.info(f"Found {len(districts_spread)} districts in County rate spread file")
    except Exception as e:
        logger.error(f"Error reading County rate spread file: {str(e)}")
        districts_spread = []
    
    # Combine all district names from different sources
    all_districts = set()
    
    # Add districts from levy worksheets
    for file in worksheet_files:
        district_name = file.replace("2025.xlsx", "").strip()
        district_name = district_name.replace(" - linked", "").replace(" - unlinked", "")
        all_districts.add(district_name)
    
    # Add districts from other sources
    all_districts.update(districts_590)
    all_districts.update(districts_const)
    all_districts.update(districts_spread)
    
    logger.info(f"Found {len(all_districts)} unique districts in total")
    
    # Process each unique district
    for district_name in all_districts:
        try:
            logger.info(f"Processing district: {district_name}")
            
            # Skip empty or clearly incorrect district names
            if not district_name or district_name.lower() in ['nan', 'none', 'unnamed', 'total']:
                continue
                
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
            
            # Create district code from name
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
                filename="multiple_sources",
                import_type=ImportType.TAX_DISTRICT,
                status="COMPLETED",
                notes=f"Imported district {district_name}",
                user_id=admin_user.id if admin_user else None
            )
            
        except Exception as e:
            logger.error(f"Error processing district {district_name}: {str(e)}")
            db.session.rollback()
            
            # Log the error
            create_import_log(
                filename="multiple_sources",
                import_type=ImportType.TAX_DISTRICT,
                status="FAILED",
                notes=f"Error importing district {district_name}: {str(e)}",
                user_id=admin_user.id if admin_user else None
            )
    
    logger.info("Completed importing tax districts")


def import_tax_codes_from_cert_report():
    """Import tax codes from certification report."""
    logger.info("Importing tax codes from certification report")
    
    admin_user = get_admin_user()
    success_count = 0
    import_log = None
    
    try:
        # Use Tax Collection file from Certification to Treasurer folder
        cert_file = "Tax Collection 2025.xlsx"
        file_path = os.path.join(CERTIFICATION_DIR, cert_file)
        
        if not os.path.exists(file_path):
            logger.warning(f"Tax Collection file {cert_file} not found")
            return
        
        # Create import log
        import_log = create_import_log(
            filename=cert_file,
            import_type=ImportType.TAX_CODE,
            status="PROCESSING",
            notes="Started processing tax codes from Tax Collection file",
            user_id=admin_user.id if admin_user else None
        )
        
        # Read the certification file
        df = pd.read_excel(file_path)
        
        # Get all districts from the database
        districts = TaxDistrict.query.filter_by(county=COUNTY_NAME, state=STATE_CODE, year=YEAR).all()
        district_map = {d.district_name.lower(): d for d in districts}
        
        # Find the header row that contains "TAXING DISTRICT" 
        taxing_district_row = None
        for idx, row in df.iterrows():
            for col in df.columns:
                val = str(row[col]).strip().upper() if pd.notna(row[col]) else ""
                if "TAXING DISTRICT" in val:
                    taxing_district_row = idx
                    break
            if taxing_district_row is not None:
                break
        
        if taxing_district_row is None:
            logger.warning("Could not find TAXING DISTRICT row in Tax Collection file")
            import_log.status = "FAILED"
            import_log.notes = "Could not find TAXING DISTRICT row in Tax Collection file"
            db.session.commit()
            return
        
        # Find the relevant columns
        district_col = None
        valuation_col = None
        rate_col = None
        amount_col = None
        
        # Identify columns by their headers
        for col in df.columns:
            col_val = str(df.iloc[taxing_district_row][col]).strip().upper() if pd.notna(df.iloc[taxing_district_row][col]) else ""
            if "TAXING DISTRICT" in col_val:
                district_col = col
            elif "LEVY VALUATION" in col_val:
                valuation_col = col
            elif "$/1000" in col_val:
                rate_col = col
            elif "AMOUNT TO BE" in col_val or "COLLECTED" in col_val:
                amount_col = col
        
        if not all([district_col, valuation_col, rate_col, amount_col]):
            missing = []
            if not district_col: missing.append("TAXING DISTRICT")
            if not valuation_col: missing.append("LEVY VALUATION")
            if not rate_col: missing.append("$/1000")
            if not amount_col: missing.append("AMOUNT TO BE COLLECTED")
            
            logger.warning(f"Could not find all required columns: {', '.join(missing)}")
            import_log.status = "FAILED"
            import_log.notes = f"Could not find all required columns: {', '.join(missing)}"
            db.session.commit()
            return
        
        # Start processing from the row after headers
        start_row = taxing_district_row + 2  # Skip the header row and any title rows
        
        # Process each row in the tax collection file
        for idx, row in df.iloc[start_row:].iterrows():
            try:
                district_name = str(row[district_col]).strip() if pd.notna(row[district_col]) else ""
                
                # Skip empty rows and headers/titles
                if not district_name or district_name.lower() in ['nan', 'none', 'total', 'grand total']:
                    continue
                
                # Some rows might not have all values
                if not pd.notna(row[valuation_col]) or not pd.notna(row[rate_col]) or not pd.notna(row[amount_col]):
                    logger.warning(f"Incomplete data for district {district_name}, skipping")
                    continue
                
                # Extract values
                valuation = float(row[valuation_col])
                rate = float(row[rate_col])
                levy_amount = float(row[amount_col])
                
                # Find matching district in database
                district = None
                district_name_lower = district_name.lower()
                
                # Try direct match
                if district_name_lower in district_map:
                    district = district_map[district_name_lower]
                else:
                    # Try partial match
                    for name, dist in district_map.items():
                        if district_name_lower in name or name in district_name_lower:
                            district = dist
                            break
                
                if not district:
                    # Create a new district if not found
                    logger.warning(f"District '{district_name}' not found in database, creating new record")
                    district_type = guess_district_type(district_name)
                    district_code = district_name.replace(" ", "_").lower()[:16]
                    
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
                    
                    # Update the district map
                    district_map[district_name.lower()] = district
                
                # Generate a tax code for this district
                tax_code_val = f"BENT{district.id:04d}"
                
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
                    # Update the values
                    existing_code.total_assessed_value = valuation
                    existing_code.effective_tax_rate = rate
                    existing_code.total_levy_amount = levy_amount
                    db.session.commit()
                    continue
                
                # Create the tax code
                tax_code = TaxCode(
                    tax_code=tax_code_val,
                    tax_district_id=district.id,
                    description=f"Tax code for {district.district_name}",
                    total_assessed_value=valuation,
                    effective_tax_rate=rate,
                    total_levy_amount=levy_amount,
                    year=YEAR,
                    created_by_id=admin_user.id if admin_user else None
                )
                
                db.session.add(tax_code)
                success_count += 1
                
                # Create historical rate record
                historical_rate = TaxCodeHistoricalRate(
                    tax_code_id=tax_code.id,
                    year=YEAR,
                    levy_rate=rate,
                    levy_amount=levy_amount,
                    total_assessed_value=valuation,
                    created_by_id=admin_user.id if admin_user else None
                )
                
                db.session.add(historical_rate)
                
                # Commit every 10 records to avoid large transactions
                if success_count % 10 == 0:
                    db.session.commit()
                    logger.info(f"Committed {success_count} tax codes")
                
            except Exception as e:
                logger.warning(f"Error processing row for district {district_name if 'district_name' in locals() else 'unknown'}: {str(e)}")
        
        # Final commit
        db.session.commit()
        
        # Update import log
        if import_log:
            import_log.status = "COMPLETED"
            import_log.notes = f"Successfully imported {success_count} tax codes"
            db.session.commit()
        
        logger.info(f"Completed importing {success_count} tax codes")
        
    except Exception as e:
        logger.error(f"Error importing tax codes: {str(e)}")
        db.session.rollback()
        
        # Update import log if it exists
        if import_log:
            import_log.status = "FAILED"
            import_log.notes = f"Error: {str(e)}"
            db.session.commit()


def import_levy_rates():
    """Import levy rates from levy reports."""
    logger.info("Importing levy rates from all available sources")
    
    admin_user = get_admin_user()
    success_count = 0
    
    # Get all tax districts and codes for the county and year
    districts = TaxDistrict.query.filter_by(county=COUNTY_NAME, state=STATE_CODE, year=YEAR).all()
    district_map = {d.district_name.lower(): d for d in districts}
    
    tax_codes = TaxCode.query.join(TaxDistrict).filter(
        and_(
            TaxDistrict.county == COUNTY_NAME,
            TaxDistrict.state == STATE_CODE,
            TaxCode.year == YEAR
        )
    ).all()
    
    tax_code_by_district = {}
    for tc in tax_codes:
        if tc.tax_district_id not in tax_code_by_district:
            tax_code_by_district[tc.tax_district_id] = tc
    
    # 1. Import rates from 5.90 file
    try:
        file_path = os.path.join(DATA_DIR, "5.90.xlsx")
        if os.path.exists(file_path):
            logger.info(f"Processing levy rates from 5.90 file")
            
            # Create import log
            import_log = create_import_log(
                filename="5.90.xlsx",
                import_type=ImportType.RATE,
                status="PROCESSING",
                notes="Processing levy rates from 5.90 file",
                user_id=admin_user.id if admin_user else None
            )
            
            df_590 = pd.read_excel(file_path)
            
            # Find the relevant columns
            tax_district_col = None
            levy_rate_col = None
            
            # The format has "Tax District" and "Levy Rate" as headers
            for col in df_590.columns:
                col_values = df_590[col].astype(str).str.lower()
                if col_values.str.contains('tax district').any():
                    tax_district_col = col
                elif col_values.str.contains('levy rate').any():
                    levy_rate_col = col
            
            if tax_district_col is None or levy_rate_col is None:
                logger.warning("Could not find required columns in 5.90 file")
                if import_log:
                    import_log.status = "FAILED"
                    import_log.notes = "Could not find required columns in 5.90 file"
                    db.session.commit()
            else:
                # Find the row with column headers
                header_idx = None
                for idx, row in df_590.iterrows():
                    if str(row[tax_district_col]).strip().lower() == "tax district":
                        header_idx = idx
                        break
                
                if header_idx is not None:
                    # Process each row after the header
                    file_success_count = 0
                    for idx, row in df_590.iloc[header_idx+1:].iterrows():
                        try:
                            district_name = str(row[tax_district_col]).strip() if pd.notna(row[tax_district_col]) else ""
                            
                            # Skip empty rows or non-data rows
                            if not district_name or district_name.lower() in ['nan', 'none', 'total', 'unnamed']:
                                continue
                            
                            # Skip if rate is missing
                            if not pd.notna(row[levy_rate_col]):
                                continue
                            
                            levy_rate = float(row[levy_rate_col])
                            
                            # Find the district
                            district_name_lower = district_name.lower()
                            district = None
                            
                            # Try direct match
                            if district_name_lower in district_map:
                                district = district_map[district_name_lower]
                            else:
                                # Try partial match
                                for name, dist in district_map.items():
                                    if district_name_lower in name or name in district_name_lower:
                                        district = dist
                                        break
                            
                            if not district:
                                logger.warning(f"District '{district_name}' not found in database, skipping")
                                continue
                            
                            # Find the tax code for this district
                            if district.id not in tax_code_by_district:
                                logger.warning(f"No tax code found for district '{district_name}', skipping")
                                continue
                            
                            tax_code = tax_code_by_district[district.id]
                            
                            # Update the tax code with the levy rate
                            tax_code.effective_tax_rate = levy_rate
                            
                            # Update or create historical rate record
                            existing_rate = TaxCodeHistoricalRate.query.filter(
                                and_(
                                    TaxCodeHistoricalRate.tax_code_id == tax_code.id,
                                    TaxCodeHistoricalRate.year == YEAR
                                )
                            ).first()
                            
                            if existing_rate:
                                # Update the existing rate
                                existing_rate.levy_rate = levy_rate
                                # Keep the existing levy_amount and total_assessed_value if available
                                if not existing_rate.total_assessed_value and tax_code.total_assessed_value:
                                    existing_rate.total_assessed_value = tax_code.total_assessed_value
                                if not existing_rate.levy_amount and tax_code.total_levy_amount:
                                    existing_rate.levy_amount = tax_code.total_levy_amount
                            else:
                                # Create a new historical rate record
                                historical_rate = TaxCodeHistoricalRate(
                                    tax_code_id=tax_code.id,
                                    year=YEAR,
                                    levy_rate=levy_rate,
                                    levy_amount=tax_code.total_levy_amount,
                                    total_assessed_value=tax_code.total_assessed_value,
                                    created_by_id=admin_user.id if admin_user else None
                                )
                                db.session.add(historical_rate)
                            
                            file_success_count += 1
                            success_count += 1
                            
                            # Commit every 20 records
                            if file_success_count % 20 == 0:
                                db.session.commit()
                                logger.info(f"Committed {file_success_count} records from 5.90 file")
                        
                        except Exception as e:
                            logger.warning(f"Error processing row for district {district_name if 'district_name' in locals() else 'unknown'}: {str(e)}")
                    
                    # Commit remaining records
                    db.session.commit()
                    
                    # Update import log
                    if import_log:
                        import_log.status = "COMPLETED"
                        import_log.notes = f"Successfully imported {file_success_count} levy rates from 5.90 file"
                        db.session.commit()
                    
                    logger.info(f"Completed importing {file_success_count} levy rates from 5.90 file")
                else:
                    logger.warning("Could not find header row in 5.90 file")
                    if import_log:
                        import_log.status = "FAILED"
                        import_log.notes = "Could not find header row in 5.90 file"
                        db.session.commit()
    
    except Exception as e:
        logger.error(f"Error processing 5.90 file: {str(e)}")
        db.session.rollback()
        if 'import_log' in locals() and import_log:
            import_log.status = "FAILED"
            import_log.notes = f"Error: {str(e)}"
            db.session.commit()
    
    # 2. Import rates from Constitutional 1% file
    try:
        file_path = os.path.join(DATA_DIR, "2025 Constitutional 1%.xlsx")
        if os.path.exists(file_path):
            logger.info(f"Processing levy rates from Constitutional 1% file")
            
            # Create import log
            import_log = create_import_log(
                filename="2025 Constitutional 1%.xlsx",
                import_type=ImportType.RATE,
                status="PROCESSING",
                notes="Processing levy rates from Constitutional 1% file",
                user_id=admin_user.id if admin_user else None
            )
            
            df_const = pd.read_excel(file_path)
            
            # Find the relevant columns
            tax_district_col = None
            levy_rate_col = None
            
            # The format has "Tax District" and "Levy Rate" as headers
            for col in df_const.columns:
                col_values = df_const[col].astype(str).str.lower()
                if col_values.str.contains('tax district').any():
                    tax_district_col = col
                elif col_values.str.contains('levy rate').any():
                    levy_rate_col = col
            
            if tax_district_col is None or levy_rate_col is None:
                logger.warning("Could not find required columns in Constitutional 1% file")
                if import_log:
                    import_log.status = "FAILED"
                    import_log.notes = "Could not find required columns in Constitutional 1% file"
                    db.session.commit()
            else:
                # Find the row with column headers
                header_idx = None
                for idx, row in df_const.iterrows():
                    if str(row[tax_district_col]).strip().lower() == "tax district":
                        header_idx = idx
                        break
                
                if header_idx is not None:
                    # Process each row after the header
                    file_success_count = 0
                    for idx, row in df_const.iloc[header_idx+1:].iterrows():
                        try:
                            district_name = str(row[tax_district_col]).strip() if pd.notna(row[tax_district_col]) else ""
                            
                            # Skip empty rows or non-data rows
                            if not district_name or district_name.lower() in ['nan', 'none', 'total', 'unnamed']:
                                continue
                            
                            # Skip if rate is missing
                            if not pd.notna(row[levy_rate_col]):
                                continue
                            
                            levy_rate = float(row[levy_rate_col])
                            
                            # Find the district
                            district_name_lower = district_name.lower()
                            district = None
                            
                            # Try direct match
                            if district_name_lower in district_map:
                                district = district_map[district_name_lower]
                            else:
                                # Try partial match
                                for name, dist in district_map.items():
                                    if district_name_lower in name or name in district_name_lower:
                                        district = dist
                                        break
                            
                            if not district:
                                logger.warning(f"District '{district_name}' not found in database, skipping")
                                continue
                            
                            # Find the tax code for this district
                            if district.id not in tax_code_by_district:
                                logger.warning(f"No tax code found for district '{district_name}', skipping")
                                continue
                            
                            tax_code = tax_code_by_district[district.id]
                            
                            # Update the tax code with the levy rate if it's not set already
                            if not tax_code.effective_tax_rate:
                                tax_code.effective_tax_rate = levy_rate
                            
                            # Update or create historical rate record
                            existing_rate = TaxCodeHistoricalRate.query.filter(
                                and_(
                                    TaxCodeHistoricalRate.tax_code_id == tax_code.id,
                                    TaxCodeHistoricalRate.year == YEAR
                                )
                            ).first()
                            
                            if existing_rate:
                                # Only update if the existing rate is not set
                                if not existing_rate.levy_rate:
                                    existing_rate.levy_rate = levy_rate
                            else:
                                # Create a new historical rate record
                                historical_rate = TaxCodeHistoricalRate(
                                    tax_code_id=tax_code.id,
                                    year=YEAR,
                                    levy_rate=levy_rate,
                                    levy_amount=tax_code.total_levy_amount,
                                    total_assessed_value=tax_code.total_assessed_value,
                                    created_by_id=admin_user.id if admin_user else None
                                )
                                db.session.add(historical_rate)
                            
                            file_success_count += 1
                            success_count += 1
                            
                            # Commit every 20 records
                            if file_success_count % 20 == 0:
                                db.session.commit()
                                logger.info(f"Committed {file_success_count} records from Constitutional 1% file")
                        
                        except Exception as e:
                            logger.warning(f"Error processing row for district {district_name if 'district_name' in locals() else 'unknown'}: {str(e)}")
                    
                    # Commit remaining records
                    db.session.commit()
                    
                    # Update import log
                    if import_log:
                        import_log.status = "COMPLETED"
                        import_log.notes = f"Successfully imported {file_success_count} levy rates from Constitutional 1% file"
                        db.session.commit()
                    
                    logger.info(f"Completed importing {file_success_count} levy rates from Constitutional 1% file")
                else:
                    logger.warning("Could not find header row in Constitutional 1% file")
                    if import_log:
                        import_log.status = "FAILED"
                        import_log.notes = "Could not find header row in Constitutional 1% file"
                        db.session.commit()
    
    except Exception as e:
        logger.error(f"Error processing Constitutional 1% file: {str(e)}")
        db.session.rollback()
        if 'import_log' in locals() and import_log:
            import_log.status = "FAILED"
            import_log.notes = f"Error: {str(e)}"
            db.session.commit()
    
    # Calculate levy amount if missing but we have rate and assessed value
    try:
        for tax_code in tax_codes:
            if (tax_code.effective_tax_rate and tax_code.total_assessed_value and 
                (not tax_code.total_levy_amount or tax_code.total_levy_amount == 0)):
                # Calculate levy amount (rate is per $1000 of assessed value)
                tax_code.total_levy_amount = tax_code.effective_tax_rate * tax_code.total_assessed_value / 1000
                
                # Update historical record if it exists
                existing_rate = TaxCodeHistoricalRate.query.filter(
                    and_(
                        TaxCodeHistoricalRate.tax_code_id == tax_code.id,
                        TaxCodeHistoricalRate.year == YEAR
                    )
                ).first()
                
                if existing_rate and (not existing_rate.levy_amount or existing_rate.levy_amount == 0):
                    existing_rate.levy_amount = tax_code.total_levy_amount
        
        # Commit the calculated values
        db.session.commit()
        logger.info("Updated calculated levy amounts based on rates and assessed values")
    
    except Exception as e:
        logger.error(f"Error calculating missing levy amounts: {str(e)}")
        db.session.rollback()
    
    logger.info(f"Completed importing levy rates from all sources, total: {success_count}")


def import_preliminary_values():
    """Import preliminary assessed values."""
    logger.info("Importing preliminary assessed values")
    
    admin_user = get_admin_user()
    success_count = 0
    import_log = None
    
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
        # If no preliminary values files found, try other files that might contain assessed values
        prelim_files = [f for f in os.listdir(PRELIMINARY_VALUES_DIR) 
                      if f.endswith('.xlsx') or f.endswith('.xls')]
    
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
            notes=f"Started processing preliminary values from {prelim_file}",
            user_id=admin_user.id if admin_user else None
        )
        
        # Read the preliminary values file
        df = pd.read_excel(file_path)
        
        # Get all districts for the county and year
        districts = TaxDistrict.query.filter_by(county=COUNTY_NAME, state=STATE_CODE, year=YEAR).all()
        district_map = {d.district_name.lower(): d for d in districts}
        
        # Get all tax codes for the districts
        tax_codes = TaxCode.query.join(TaxDistrict).filter(
            and_(
                TaxDistrict.county == COUNTY_NAME,
                TaxDistrict.state == STATE_CODE,
                TaxCode.year == YEAR
            )
        ).all()
        tax_code_by_district = {}
        for tc in tax_codes:
            if tc.tax_district_id not in tax_code_by_district:
                tax_code_by_district[tc.tax_district_id] = tc
        
        # Try to find district name and assessed value columns
        # This is challenging without knowing the exact format, so we'll search for columns
        # containing terms like "district", "value", "assessed", etc.
        
        # Potential columns for district name
        district_col = None
        for col in df.columns:
            col_name = str(col).lower()
            if any(term in col_name for term in ['district', 'taxing', 'authority', 'entity']):
                district_col = col
                break
        
        # If we couldn't find a clear district column, try the first column
        if district_col is None and len(df.columns) > 0:
            district_col = df.columns[0]
        
        # Potential columns for assessed value
        value_col = None
        for col in df.columns:
            col_name = str(col).lower()
            if any(term in col_name for term in ['value', 'assessed', 'valuation', 'av']):
                value_col = col
                break
        
        # If we couldn't find a clear value column, try the numeric columns
        if value_col is None:
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    value_col = col
                    break
        
        if district_col is None or value_col is None:
            logger.warning(f"Could not identify district and value columns in {prelim_file}")
            if import_log:
                import_log.status = "FAILED"
                import_log.notes = f"Could not identify district and value columns in {prelim_file}"
                db.session.commit()
            return
        
        # Process each row, looking for district names and assessed values
        for idx, row in df.iterrows():
            try:
                district_name = str(row[district_col]).strip() if pd.notna(row[district_col]) else ""
                
                # Skip empty rows or non-data rows
                if not district_name or district_name.lower() in ['nan', 'none', 'total', 'grand total', 'unnamed']:
                    continue
                
                # Skip if assessed value is missing
                if not pd.notna(row[value_col]):
                    continue
                
                assessed_value = float(row[value_col])
                
                # Skip unreasonable values (e.g., 0 or negative)
                if assessed_value <= 0:
                    continue
                
                # Find the district
                district_name_lower = district_name.lower()
                district = None
                
                # Try direct match
                if district_name_lower in district_map:
                    district = district_map[district_name_lower]
                else:
                    # Try partial match
                    for name, dist in district_map.items():
                        if district_name_lower in name or name in district_name_lower:
                            district = dist
                            break
                
                if not district:
                    logger.warning(f"District '{district_name}' not found in database, skipping")
                    continue
                
                # Find the tax code for this district
                if district.id not in tax_code_by_district:
                    logger.warning(f"No tax code found for district '{district_name}', skipping")
                    continue
                
                tax_code = tax_code_by_district[district.id]
                
                # Update the tax code with the assessed value
                if not tax_code.total_assessed_value or tax_code.total_assessed_value <= 0:
                    tax_code.total_assessed_value = assessed_value
                    
                    # Update historical rate record if it exists
                    existing_rate = TaxCodeHistoricalRate.query.filter(
                        and_(
                            TaxCodeHistoricalRate.tax_code_id == tax_code.id,
                            TaxCodeHistoricalRate.year == YEAR
                        )
                    ).first()
                    
                    if existing_rate:
                        existing_rate.total_assessed_value = assessed_value
                        
                        # Calculate levy amount if we have a rate but no amount
                        if existing_rate.levy_rate and (not existing_rate.levy_amount or existing_rate.levy_amount == 0):
                            existing_rate.levy_amount = existing_rate.levy_rate * assessed_value / 1000
                
                success_count += 1
                
                # Commit every 20 records
                if success_count % 20 == 0:
                    db.session.commit()
                    logger.info(f"Committed {success_count} assessed values")
            
            except Exception as e:
                logger.warning(f"Error processing row for district {district_name if 'district_name' in locals() else 'unknown'}: {str(e)}")
        
        # Final commit
        db.session.commit()
        
        # Update import log
        if import_log:
            import_log.status = "COMPLETED"
            import_log.notes = f"Successfully imported {success_count} assessed values"
            db.session.commit()
        
        logger.info(f"Completed importing {success_count} assessed values")
        
    except Exception as e:
        logger.error(f"Error importing preliminary values: {str(e)}")
        db.session.rollback()
        
        # Update import log if it exists
        if import_log:
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