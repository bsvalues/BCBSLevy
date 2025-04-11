"""
Integration file to add MCP Army system to the Flask application.

This module updates the app.py file to initialize and integrate the MCP Army
system with the existing application.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_app_py():
    """
    Update the app.py file to initialize the MCP Army system.
    """
    app_py_path = Path('app.py')
    if not app_py_path.exists():
        logger.error("app.py file not found")
        return False
    
    # Read the app.py file
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Create backup
    backup_path = f'app.py.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}'
    with open(backup_path, 'w') as f:
        f.write(content)
    logger.info(f"Created backup of app.py at {backup_path}")
    
    # Update the imports section
    import_marker = "from utils.advanced_ai_agent import init_advanced_agent"
    if import_marker in content:
        updated_imports = import_marker + "\n    from utils.mcp_army_init import init_mcp_army"
        content = content.replace(import_marker, updated_imports)
    else:
        logger.error("Could not find import marker in app.py")
        return False
    
    # Update the initialization section
    init_marker = "# Initialize Advanced AI Agent with dedicated error handling"
    if init_marker in content:
        init_section = """
    # Initialize MCP Army system with dedicated error handling
    try:
        if api_status['status'] == 'valid':
            mcp_army_initialized = init_mcp_army(app)
            if mcp_army_initialized:
                app.logger.info("MCP Army system initialized successfully")
            else:
                app.logger.warning("MCP Army system initialization failed")
        else:
            app.logger.warning("Skipping MCP Army initialization due to API key issues")
    except ImportError as e:
        app.logger.error(f"Error importing MCP Army dependencies: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error initializing MCP Army system: {str(e)}")
        app.logger.error("MCP Army features will be unavailable")
        
    # Initialize Advanced AI Agent with dedicated error handling"""
        
        content = content.replace(init_marker, init_section)
    else:
        logger.error("Could not find initialization marker in app.py")
        return False
    
    # Update the registration section
    register_marker = "# Initialize MCP routes"
    register_update = """# Initialize MCP routes
    init_mcp_routes(app)
    
    # Initialize MCP Army routes
    try:
        from routes_mcp_army import register_mcp_army_routes
        register_mcp_army_routes(app)
        app.logger.info("MCP Army routes registered")
    except ImportError as e:
        app.logger.error(f"Error importing MCP Army routes: {str(e)}")
    except Exception as e:
        app.logger.error(f"Error registering MCP Army routes: {str(e)}")"""
    
    if register_marker in content:
        content = content.replace(f"{register_marker}\n    init_mcp_routes(app)", register_update)
    else:
        logger.error("Could not find route registration marker in app.py")
        return False
    
    # Write the updated content
    with open(app_py_path, 'w') as f:
        f.write(content)
    
    logger.info("Updated app.py with MCP Army integration")
    return True

if __name__ == "__main__":
    update_app_py()