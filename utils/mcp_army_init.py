"""
MCP Army initialization module.

This module provides functions for initializing the MCP Army system
and integrating it with Flask.
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Union

from flask import Flask

from utils.mcp_agent_manager import AgentManager
from utils.mcp_experience import MCPCollaborationManager

# Setup logging
logger = logging.getLogger(__name__)

# Global instances
agent_manager = None
collaboration_manager = None

def init_mcp_army(app: Optional[Flask] = None) -> bool:
    """
    Initialize the MCP Army system.
    
    Args:
        app: Optional Flask application instance
        
    Returns:
        True if initialization was successful, False otherwise
    """
    global agent_manager, collaboration_manager
    
    logger.info("Initializing MCP Army system")
    
    try:
        # Initialize collaboration manager
        collaboration_manager = MCPCollaborationManager()
        
        # Initialize agent manager
        agent_manager = AgentManager(collaboration_manager)
        
        # Initialize agents
        army_initialized = agent_manager.initialize_agent_army()
        if not army_initialized:
            logger.error("Failed to initialize Agent Army")
            return False
        
        # Start agent monitoring
        agent_manager.start_monitoring(interval=60.0)
        
        # Register with Flask app if provided
        if app:
            app.config['MCP_ARMY_INITIALIZED'] = True
            app.config['MCP_ARMY_AGENT_MANAGER'] = agent_manager
            app.config['MCP_ARMY_COLLABORATION_MANAGER'] = collaboration_manager
        
        logger.info("MCP Army system initialized successfully")
        return True
        
    except ImportError as e:
        logger.error(f"Error importing MCP Army dependencies: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error initializing MCP Army system: {str(e)}")
        return False

def get_agent_manager() -> Optional[AgentManager]:
    """
    Get the global AgentManager instance.
    
    Returns:
        The global AgentManager instance or None if not initialized
    """
    global agent_manager
    return agent_manager

def get_collaboration_manager() -> Optional[MCPCollaborationManager]:
    """
    Get the global MCPCollaborationManager instance.
    
    Returns:
        The global MCPCollaborationManager instance or None if not initialized
    """
    global collaboration_manager
    return collaboration_manager