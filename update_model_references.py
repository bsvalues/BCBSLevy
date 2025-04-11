"""
Model reference update script for the Levy Calculation System.

This script updates model definitions in code to match the updated database structure
after migrating foreign key references from tax_district_old to tax_district.
"""

import os
import re
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"migration_reports/model_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Files to check for model references
MODEL_FILES = [
    'models.py',
    'routes_forecasting.py',
    'routes_levy_calculator.py',
    'utils/forecasting_utils.py',
    'utils/levy_calculation_utils.py',
    'utils/compliance_utils.py'
]

def create_backup(filepath):
    """Create a backup of the file before modifying it."""
    if not os.path.exists(filepath):
        return False
    
    backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        with open(filepath, 'r') as f_in:
            content = f_in.read()
        
        with open(backup_path, 'w') as f_out:
            f_out.write(content)
        
        logger.info(f"Created backup of {filepath} at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating backup of {filepath}: {e}")
        return False

def update_model_references(filepath):
    """Update references to tax_district_old in a file."""
    if not os.path.exists(filepath):
        logger.warning(f"File {filepath} does not exist")
        return False
    
    try:
        # Create backup first
        if not create_backup(filepath):
            logger.error(f"Failed to create backup for {filepath}, skipping update")
            return False
        
        # Read file content
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for tax_district_old references
        has_old_refs = 'tax_district_old' in content
        
        if not has_old_refs:
            logger.info(f"No tax_district_old references found in {filepath}")
            return True
        
        # Update ForeignKey references
        updated_content = re.sub(
            r'ForeignKey\([\'"]tax_district_old[.\w]*[\'"]\)',
            r'ForeignKey(\'tax_district.id\')',
            content
        )
        
        # Update relationship definitions
        updated_content = re.sub(
            r'relationship\([\'"]TaxDistrictOld[\'"]',
            r'relationship(\'TaxDistrict\'',
            updated_content
        )
        
        # Update model references
        updated_content = re.sub(
            r'TaxDistrictOld\.',
            r'TaxDistrict.',
            updated_content
        )
        
        # Write updated content
        with open(filepath, 'w') as f:
            f.write(updated_content)
        
        logger.info(f"Updated tax_district references in {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error updating {filepath}: {e}")
        return False

def scan_directories():
    """Scan directories for additional files that might contain references."""
    found_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments, .git, and other irrelevant directories
        if any(skip in root for skip in ['.git', '__pycache__', 'venv', 'env', 'node_modules', 'migrations']):
            continue
        
        for file in files:
            if file.endswith('.py') and file not in [os.path.basename(f) for f in MODEL_FILES]:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if 'tax_district_old' in content:
                            found_files.append(filepath)
                except Exception:
                    # Skip files that can't be read
                    pass
    
    return found_files

def run_update():
    """Run the model reference update process."""
    logger.info("Starting model reference update")
    
    # Create migration_reports directory if it doesn't exist
    os.makedirs("migration_reports", exist_ok=True)
    
    # Update known model files
    success_count = 0
    for filepath in MODEL_FILES:
        if update_model_references(filepath):
            success_count += 1
    
    logger.info(f"Updated {success_count}/{len(MODEL_FILES)} known model files")
    
    # Scan for additional files
    additional_files = scan_directories()
    if additional_files:
        logger.info(f"Found {len(additional_files)} additional files with tax_district_old references:")
        for filepath in additional_files:
            logger.info(f"  - {filepath}")
        
        # Prompt for confirmation
        logger.info("Would you like to update these files? (y/n)")
        if input().lower() == 'y':
            additional_success = 0
            for filepath in additional_files:
                if update_model_references(filepath):
                    additional_success += 1
            logger.info(f"Updated {additional_success}/{len(additional_files)} additional files")
    else:
        logger.info("No additional files with tax_district_old references found")
    
    logger.info("Model reference update completed")
    return True

if __name__ == "__main__":
    if run_update():
        sys.exit(0)
    else:
        sys.exit(1)