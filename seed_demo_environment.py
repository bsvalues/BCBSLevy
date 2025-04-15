"""
Demo Environment Setup Script for LevyMaster 24-Hour Demo

This script sets up a comprehensive demo environment with:
1. Demo user accounts with different permission levels
2. Realistic tax districts based on Benton County data
3. Sample properties with appropriate assessment values
4. Historical data showing year-over-year trends
5. Sample levy scenarios for demonstration
"""

import os
import sys
import logging
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app import app, db
from models import User, TaxDistrict, TaxCode, TaxCodeHistoricalRate, Property, LevyScenario

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Demo user account data
DEMO_USERS = [
    {
        "username": "admin",
        "email": "admin@levymaster.gov",
        "password": "admin123",  # In production, use secure passwords
        "first_name": "Admin",
        "last_name": "User",
        "is_admin": True,
        "is_active": True,
        "role": "Administrator",
        "department": "Information Technology"
    },
    {
        "username": "assessor",
        "email": "assessor@levymaster.gov",
        "password": "assessor123",
        "first_name": "Jane",
        "last_name": "Assessor",
        "is_admin": False,
        "is_active": True,
        "role": "Assessor",
        "department": "County Assessor's Office"
    },
    {
        "username": "viewer",
        "email": "viewer@levymaster.gov",
        "password": "viewer123",
        "first_name": "View",
        "last_name": "Only",
        "is_admin": False,
        "is_active": True,
        "role": "Report Viewer",
        "department": "Finance"
    }
]

# Sample Benton County tax districts
BENTON_COUNTY_DISTRICTS = [
    {"code": "01", "name": "Benton County", "type": "County", "statutory_limit": 1.80},
    {"code": "02", "name": "City of Kennewick", "type": "City", "statutory_limit": 3.10},
    {"code": "03", "name": "City of Richland", "type": "City", "statutory_limit": 3.10},
    {"code": "04", "name": "City of Prosser", "type": "City", "statutory_limit": 3.10},
    {"code": "05", "name": "City of West Richland", "type": "City", "statutory_limit": 3.10},
    {"code": "06", "name": "City of Benton City", "type": "City", "statutory_limit": 3.10},
    {"code": "07", "name": "Kennewick School District #17", "type": "School", "statutory_limit": 1.50},
    {"code": "08", "name": "Richland School District #400", "type": "School", "statutory_limit": 1.50},
    {"code": "09", "name": "Prosser School District #116", "type": "School", "statutory_limit": 1.50},
    {"code": "10", "name": "Kiona-Benton School District #52", "type": "School", "statutory_limit": 1.50},
    {"code": "11", "name": "Finley School District #53", "type": "School", "statutory_limit": 1.50},
    {"code": "12", "name": "Benton County Fire District #1", "type": "Fire", "statutory_limit": 1.50},
    {"code": "13", "name": "Benton County Fire District #2", "type": "Fire", "statutory_limit": 1.50},
    {"code": "14", "name": "Benton County Fire District #4", "type": "Fire", "statutory_limit": 1.50},
    {"code": "15", "name": "Mid-Columbia Library District", "type": "Library", "statutory_limit": 0.50},
    {"code": "16", "name": "Benton County Mosquito Control", "type": "Special", "statutory_limit": 0.25},
    {"code": "17", "name": "Benton County Cemetery District #1", "type": "Cemetery", "statutory_limit": 0.11},
]

# Tax code data - combination of districts that form unique tax areas
def get_tax_codes(district_ids):
    """Generate sample tax codes using district combinations."""
    tax_codes = []
    
    # Kennewick area
    tax_codes.append({
        "code": "01-02-07-12-15-16",
        "district_ids": [district_ids[0], district_ids[1], district_ids[6], district_ids[11], district_ids[14], district_ids[15]], 
        "description": "Kennewick Urban Area",
        "levy_rate": 9.76
    })
    
    # Richland area
    tax_codes.append({
        "code": "01-03-08-13-15-16",
        "district_ids": [district_ids[0], district_ids[2], district_ids[7], district_ids[12], district_ids[14], district_ids[15]],
        "description": "Richland Urban Area",
        "levy_rate": 9.82
    })
    
    # Prosser area
    tax_codes.append({
        "code": "01-04-09-14-15-16-17",
        "district_ids": [district_ids[0], district_ids[3], district_ids[8], district_ids[13], district_ids[14], district_ids[15], district_ids[16]],
        "description": "Prosser Urban Area",
        "levy_rate": 10.05
    })
    
    # West Richland area
    tax_codes.append({
        "code": "01-05-08-13-15-16",
        "district_ids": [district_ids[0], district_ids[4], district_ids[7], district_ids[12], district_ids[14], district_ids[15]],
        "description": "West Richland Urban Area",
        "levy_rate": 9.71
    })
    
    # Benton City area
    tax_codes.append({
        "code": "01-06-10-14-15-16",
        "district_ids": [district_ids[0], district_ids[5], district_ids[9], district_ids[13], district_ids[14], district_ids[15]],
        "description": "Benton City Urban Area",
        "levy_rate": 9.58
    })
    
    # Rural areas
    tax_codes.append({
        "code": "01-08-13-15-16",
        "district_ids": [district_ids[0], district_ids[7], district_ids[12], district_ids[14], district_ids[15]],
        "description": "Richland Rural Area",
        "levy_rate": 6.72
    })
    
    tax_codes.append({
        "code": "01-09-14-15-16-17",
        "district_ids": [district_ids[0], district_ids[8], district_ids[13], district_ids[14], district_ids[15], district_ids[16]],
        "description": "Prosser Rural Area",
        "levy_rate": 6.95
    })
    
    tax_codes.append({
        "code": "01-11-12-15-16",
        "district_ids": [district_ids[0], district_ids[10], district_ids[11], district_ids[14], district_ids[15]],
        "description": "Finley Rural Area",
        "levy_rate": 6.67
    })
    
    return tax_codes

# Sample properties with diverse values
def generate_properties(tax_code_ids):
    """Generate sample properties with realistic values."""
    properties = []
    
    # Property types
    property_types = ["Residential", "Commercial", "Agricultural", "Industrial", "Multi-Family"]
    
    # Addresses for each tax code area
    address_prefixes = {
        0: ["123 Columbia Dr", "456 Kennewick Ave", "789 Washington St", "321 Olympia St"],  # Kennewick
        1: ["101 George Washington Way", "234 Stevens Dr", "567 Jadwin Ave", "890 Lee Blvd"],  # Richland
        2: ["111 Meade Ave", "222 7th St", "333 Wine Country Rd", "444 Bennett Ave"],  # Prosser
        3: ["555 Paradise Way", "666 Bombing Range Rd", "777 Van Giesen St", "888 Fallon Dr"],  # West Richland
        4: ["999 9th St", "1010 Hagens Rd", "1111 Grace Ave", "1212 Dale Ave"],  # Benton City
        5: ["2020 Rural Route 1", "3030 Richland Countryside", "4040 Red Mountain Rd"],  # Rural Richland
        6: ["5050 Rural Route 2", "6060 Prosser Countryside", "7070 Wine Valley Rd"],  # Rural Prosser
        7: ["8080 Rural Route 3", "9090 Finley District", "1000 E Game Farm Rd"]  # Rural Finley
    }
    
    # Generate 50-75 properties
    num_properties = random.randint(50, 75)
    for i in range(num_properties):
        tax_code_index = random.randint(0, len(tax_code_ids) - 1)
        tax_code_id = tax_code_ids[tax_code_index]
        
        # Property type
        prop_type = random.choice(property_types)
        
        # Address
        address = random.choice(address_prefixes[tax_code_index])
        house_num = random.randint(100, 9999)
        address = f"{house_num} {address.split(' ', 1)[1]}"
        
        # Land size between 0.1 and 10 acres
        land_size = round(random.uniform(0.1, 10), 2)
        
        # Assessed value based on property type
        if prop_type == "Residential":
            assessed_value = random.randint(250000, 750000)
        elif prop_type == "Commercial":
            assessed_value = random.randint(500000, 3000000)
        elif prop_type == "Agricultural":
            assessed_value = random.randint(100000, 500000)
        elif prop_type == "Industrial":
            assessed_value = random.randint(1000000, 5000000)
        else:  # Multi-Family
            assessed_value = random.randint(750000, 2500000)
        
        # Random year built between 1950 and 2024
        year_built = random.randint(1950, 2024)
        
        properties.append({
            "parcel_id": f"1-{random.randint(10000, 99999)}-{random.randint(1000, 9999)}",
            "address": address,
            "city": address_prefixes[tax_code_index][0].split(' ')[-1],
            "state": "WA",
            "zip": f"9935{random.randint(0, 9)}",
            "property_type": prop_type,
            "assessed_value": assessed_value,
            "land_size": land_size,
            "year_built": year_built,
            "tax_code_id": tax_code_id,
            "is_exempt": False
        })
    
    return properties

# Generate historical rates for tax codes
def generate_historical_rates(tax_code_ids):
    """Generate historical tax rates for 2022-2024."""
    historical_rates = []
    
    # Years to generate data for
    years = [2022, 2023, 2024]
    
    for tax_code_id in tax_code_ids:
        for year in years:
            # Base rate - slightly different each year
            base_rate = 9.5 + random.uniform(-0.5, 0.5)
            
            # For older years, rates were generally higher
            year_adjustment = (2025 - year) * 0.15
            adjusted_rate = round(base_rate + year_adjustment, 4)
            
            # Random assessed value based on year
            base_value = 5000000000  # 5 billion base
            annual_growth = 0.03  # 3% annual growth
            year_growth_factor = (1 + annual_growth) ** (year - 2022)
            assessed_value = base_value * year_growth_factor * (1 + random.uniform(-0.01, 0.01))
            
            # Calculate levy amount
            levy_amount = adjusted_rate * (assessed_value / 1000)
            
            historical_rates.append({
                "tax_code_id": tax_code_id,
                "year": year,
                "levy_rate": adjusted_rate,
                "total_assessed_value": assessed_value,
                "levy_amount": levy_amount
            })
    
    return historical_rates

# Generate levy scenarios for demonstration
def generate_levy_scenarios(user_ids, district_ids):
    """Generate sample levy scenarios for the demo."""
    scenarios = []
    
    # Scenario 1: Current Year Baseline
    scenarios.append({
        "user_id": user_ids[0],  # Admin user
        "name": "2025 Baseline Levy Scenario",
        "description": "Baseline levy calculation for 2025 tax year using standard growth assumptions",
        "tax_district_id": district_ids[0],  # Benton County
        "year": 2025,
        "base_year": 2024,
        "target_year": 2025,
        "levy_amount": 25672458,
        "assessed_value_change": 3.2,
        "new_construction_value": 287500000,
        "annexation_value": 0,
        "result_levy_rate": 1.78,
        "result_levy_amount": 26764521,
        "is_public": True,
        "status": "FINAL"
    })
    
    # Scenario 2: New Construction Impact Analysis
    scenarios.append({
        "user_id": user_ids[1],  # Assessor user
        "name": "New Construction Impact Analysis",
        "description": "Analyzing the impact of higher than expected new construction on the county levy",
        "tax_district_id": district_ids[0],  # Benton County
        "year": 2025,
        "base_year": 2024,
        "target_year": 2025,
        "levy_amount": 25672458,
        "assessed_value_change": 3.2,
        "new_construction_value": 425000000,  # Higher new construction
        "annexation_value": 0,
        "result_levy_rate": 1.75,
        "result_levy_amount": 26892135,
        "is_public": True,
        "status": "DRAFT"
    })
    
    # Scenario 3: Multi-Year Forecast
    scenarios.append({
        "user_id": user_ids[0],  # Admin user
        "name": "2025-2027 Multi-Year Forecast",
        "description": "Three-year projection of county levy rates and amounts",
        "tax_district_id": district_ids[0],  # Benton County
        "year": 2025,
        "base_year": 2024,
        "target_year": 2027,
        "levy_amount": 25672458,
        "assessed_value_change": 3.5,
        "new_construction_value": 300000000,
        "annexation_value": 0,
        "result_levy_rate": 1.68,
        "result_levy_amount": 29126825,
        "is_public": True,
        "status": "DRAFT"
    })
    
    # Scenario 4: School District Analysis
    scenarios.append({
        "user_id": user_ids[1],  # Assessor user
        "name": "Kennewick School District Analysis",
        "description": "Analysis of school district levy with enrollment adjustments",
        "tax_district_id": district_ids[6],  # Kennewick School District
        "year": 2025,
        "base_year": 2024,
        "target_year": 2025,
        "levy_amount": 18452628,
        "assessed_value_change": 3.0,
        "new_construction_value": 125000000,
        "annexation_value": 0,
        "result_levy_rate": 1.46,
        "result_levy_amount": 19155582,
        "is_public": True,
        "status": "DRAFT"
    })
    
    # Scenario 5: Fire District Scenario
    scenarios.append({
        "user_id": user_ids[0],  # Admin user
        "name": "Fire District #1 Capital Planning",
        "description": "Long-term capital planning scenario for new equipment",
        "tax_district_id": district_ids[11],  # Fire District #1
        "year": 2025,
        "base_year": 2024,
        "target_year": 2026,
        "levy_amount": 6758421,
        "assessed_value_change": 2.8,
        "new_construction_value": 75000000,
        "annexation_value": 15000000,  # Annexation included
        "result_levy_rate": 1.38,
        "result_levy_amount": 7254862,
        "is_public": False,  # Private scenario
        "status": "DRAFT"
    })
    
    return scenarios

def seed_demo_data():
    """Main function to seed demo environment data."""
    try:
        # Create database connection
        logger.info("Starting demo environment setup...")
        
        # Create demo user accounts
        user_ids = []
        for user_data in DEMO_USERS:
            existing_user = User.query.filter_by(username=user_data["username"]).first()
            if existing_user:
                logger.info(f"User {user_data['username']} already exists, skipping")
                user_ids.append(existing_user.id)
                continue
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=generate_password_hash(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                is_admin=user_data["is_admin"],
                is_active=user_data["is_active"],
                role=user_data["role"],
                department=user_data["department"]
            )
            db.session.add(user)
            db.session.flush()  # Flush to get the ID
            user_ids.append(user.id)
            logger.info(f"Created user: {user_data['username']}")
        
        # Create tax districts
        district_ids = []
        for district_data in BENTON_COUNTY_DISTRICTS:
            existing_district = TaxDistrict.query.filter_by(district_code=district_data["code"]).first()
            if existing_district:
                logger.info(f"District {district_data['name']} already exists, skipping")
                district_ids.append(existing_district.id)
                continue
            
            district = TaxDistrict(
                district_code=district_data["code"],
                district_name=district_data["name"],
                district_type=district_data["type"],
                county="Benton",
                state="WA",
                is_active=True,
                statutory_limit=district_data["statutory_limit"],
                year=2025
            )
            db.session.add(district)
            db.session.flush()  # Flush to get the ID
            district_ids.append(district.id)
            logger.info(f"Created district: {district_data['name']}")
        
        # Create tax codes
        tax_code_ids = []
        tax_codes_data = get_tax_codes(district_ids)
        for tax_code_data in tax_codes_data:
            existing_tax_code = TaxCode.query.filter_by(tax_code=tax_code_data["code"]).first()
            if existing_tax_code:
                logger.info(f"Tax code {tax_code_data['code']} already exists, skipping")
                tax_code_ids.append(existing_tax_code.id)
                continue
            
            tax_code = TaxCode(
                tax_code=tax_code_data["code"],
                description=tax_code_data["description"],
                tax_district_id=tax_code_data["district_ids"][0],  # Use the first district as the primary
                levy_rate=tax_code_data["levy_rate"],
                total_levy_amount=0,  # Will be calculated
                effective_tax_rate=tax_code_data["levy_rate"],
                year=2025
            )
            db.session.add(tax_code)
            db.session.flush()  # Flush to get the ID
            tax_code_ids.append(tax_code.id)
            logger.info(f"Created tax code: {tax_code_data['code']}")
        
        # Create properties
        properties_data = generate_properties(tax_code_ids)
        for property_data in properties_data:
            existing_property = Property.query.filter_by(parcel_id=property_data["parcel_id"]).first()
            if existing_property:
                logger.info(f"Property {property_data['parcel_id']} already exists, skipping")
                continue
            
            property = Property(
                parcel_id=property_data["parcel_id"],
                address=property_data["address"],
                city=property_data["city"],
                state=property_data["state"],
                zip=property_data["zip"],
                property_type=property_data["property_type"],
                assessed_value=property_data["assessed_value"],
                land_size=property_data["land_size"],
                year_built=property_data["year_built"],
                tax_code_id=property_data["tax_code_id"],
                is_exempt=property_data["is_exempt"],
                year=2025
            )
            db.session.add(property)
            logger.info(f"Created property: {property_data['parcel_id']}")
        
        # Create historical tax rates
        historical_rates_data = generate_historical_rates(tax_code_ids)
        for rate_data in historical_rates_data:
            existing_rate = TaxCodeHistoricalRate.query.filter_by(
                tax_code_id=rate_data["tax_code_id"], 
                year=rate_data["year"]
            ).first()
            
            if existing_rate:
                logger.info(f"Historical rate for tax code id {rate_data['tax_code_id']} and year {rate_data['year']} already exists, skipping")
                continue
            
            historical_rate = TaxCodeHistoricalRate(
                tax_code_id=rate_data["tax_code_id"],
                year=rate_data["year"],
                levy_rate=rate_data["levy_rate"],
                total_assessed_value=rate_data["total_assessed_value"],
                levy_amount=rate_data["levy_amount"]
            )
            db.session.add(historical_rate)
            logger.info(f"Created historical rate for tax code id {rate_data['tax_code_id']} and year {rate_data['year']}")
        
        # Create levy scenarios
        scenarios_data = generate_levy_scenarios(user_ids, district_ids)
        for scenario_data in scenarios_data:
            # Check if scenario already exists with the same name and district
            existing_scenario = LevyScenario.query.filter_by(
                name=scenario_data["name"],
                tax_district_id=scenario_data["tax_district_id"],
                year=scenario_data["year"]
            ).first()
            
            if existing_scenario:
                logger.info(f"Scenario '{scenario_data['name']}' for district id {scenario_data['tax_district_id']} already exists, skipping")
                continue
            
            scenario = LevyScenario(
                user_id=scenario_data["user_id"],
                name=scenario_data["name"],
                description=scenario_data["description"],
                tax_district_id=scenario_data["tax_district_id"],
                year=scenario_data["year"],
                base_year=scenario_data["base_year"],
                target_year=scenario_data["target_year"],
                levy_amount=scenario_data["levy_amount"],
                assessed_value_change=scenario_data["assessed_value_change"],
                new_construction_value=scenario_data["new_construction_value"],
                annexation_value=scenario_data["annexation_value"],
                result_levy_rate=scenario_data["result_levy_rate"],
                result_levy_amount=scenario_data["result_levy_amount"],
                is_public=scenario_data["is_public"],
                status=scenario_data["status"]
            )
            db.session.add(scenario)
            logger.info(f"Created levy scenario: {scenario_data['name']}")
        
        # Commit all changes
        db.session.commit()
        logger.info("Demo environment setup completed successfully")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error setting up demo environment: {str(e)}")
        raise

if __name__ == "__main__":
    with app.app_context():
        seed_demo_data()