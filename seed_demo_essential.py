"""
Essential Demo Environment Setup Script for LevyMaster 24-Hour Demo

This script sets up core components for the demo environment:
1. Demo user accounts
2. Key tax districts based on Benton County
3. Essential levy scenarios for demonstration
"""

import os
import sys
import logging
from werkzeug.security import generate_password_hash

from app import app, db
from models import User, TaxDistrict, TaxCode, LevyScenario

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

# Key Benton County tax districts for the demo
BENTON_COUNTY_DISTRICTS = [
    {"code": "01", "name": "Benton County", "type": "County", "statutory_limit": 1.80},
    {"code": "02", "name": "City of Kennewick", "type": "City", "statutory_limit": 3.10},
    {"code": "03", "name": "City of Richland", "type": "City", "statutory_limit": 3.10},
    {"code": "07", "name": "Kennewick School District #17", "type": "School", "statutory_limit": 1.50},
    {"code": "12", "name": "Benton County Fire District #1", "type": "Fire", "statutory_limit": 1.50},
]

# Generate levy scenarios for demonstration
def generate_levy_scenarios(user_ids, district_ids):
    """Generate essential levy scenarios for the demo."""
    scenarios = []
    
    # Scenario 1: Current Year Baseline
    scenarios.append({
        "user_id": user_ids[0],  # Admin user
        "name": "2025 Baseline Levy",
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
        "name": "New Construction Impact",
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
    
    # Scenario 3: School District Analysis
    scenarios.append({
        "user_id": user_ids[1],  # Assessor user
        "name": "Kennewick School Levy",
        "description": "Analysis of school district levy with enrollment adjustments",
        "tax_district_id": district_ids[3],  # Kennewick School District
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
    
    return scenarios

def seed_demo_data():
    """Main function to seed essential demo data."""
    try:
        logger.info("Starting essential demo data setup...")
        
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
        
        # Create key tax districts
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
        logger.info("Essential demo data setup completed successfully")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error setting up demo data: {str(e)}")
        raise

if __name__ == "__main__":
    with app.app_context():
        seed_demo_data()