"""
MCP and Agent Army Integration Module.

This module provides the integration layer between the existing MCP framework
and the enhanced Agent Army system, enabling seamless collaboration and
communication between all components.
"""

import json
import logging
import threading
import time
from typing import Dict, List, Any, Optional, Union

from utils.mcp_core import registry, workflow_registry
from utils.mcp_experience import collaboration_manager
from utils.mcp_agent_manager import agent_manager
from utils.anthropic_utils import get_claude_service

logger = logging.getLogger(__name__)

class MCPArmyIntegration:
    """
    Integration system for MCP and the Agent Army.
    
    This class provides the necessary connections and adapters between
    the existing MCP framework and the enhanced Agent Army system, ensuring
    that all components can work together seamlessly.
    """
    
    def __init__(self):
        """Initialize the MCP and Agent Army integration system."""
        self.claude_service = get_claude_service()
        self.initialized = False
        self.initialization_lock = threading.Lock()
        
    def initialize(self) -> bool:
        """
        Initialize the integrated MCP and Agent Army system.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        with self.initialization_lock:
            if self.initialized:
                logger.info("MCP Army integration already initialized")
                return True
                
            try:
                logger.info("Initializing MCP Army integration")
                
                # Initialize the Agent Army
                agent_army_initialized = agent_manager.initialize_agent_army()
                if not agent_army_initialized:
                    logger.error("Failed to initialize Agent Army")
                    return False
                    
                # Start the agent monitoring
                agent_manager.start_monitoring(interval=60.0)
                
                # Register additional shared replay functions with MCP
                self._register_additional_functions()
                
                self.initialized = True
                logger.info("MCP Army integration initialized successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error initializing MCP Army integration: {str(e)}")
                return False
                
    def _register_additional_functions(self) -> None:
        """Register additional functions with the MCP registry."""
        # Register experience-related functions
        registry.register_function(
            func=self.get_agent_status,
            name="get_agent_status",
            description="Get the current status of an agent",
            parameter_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "ID of the agent"}
                },
                "required": ["agent_id"]
            }
        )
        
        registry.register_function(
            func=self.list_agents,
            name="list_agents",
            description="Get a list of all registered agents with their status",
            parameter_schema={
                "type": "object",
                "properties": {}
            }
        )
        
        registry.register_function(
            func=self.execute_agent_capability,
            name="execute_agent_capability",
            description="Execute a capability on a specific agent",
            parameter_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "ID of the agent"},
                    "capability": {"type": "string", "description": "Name of the capability to execute"},
                    "parameters": {"type": "object", "description": "Parameters for the capability"}
                },
                "required": ["agent_id", "capability"]
            }
        )
        
        registry.register_function(
            func=self.request_agent_assistance,
            name="request_agent_assistance",
            description="Request one agent to assist another",
            parameter_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "ID of the agent providing assistance"},
                    "target_agent": {"type": "string", "description": "ID of the agent needing assistance"},
                    "assistance_type": {"type": "string", "description": "Type of assistance needed"}
                },
                "required": ["agent_id", "target_agent"]
            }
        )
        
        registry.register_function(
            func=self.get_agent_experiences,
            name="get_agent_experiences",
            description="Get experiences from the replay buffer for an agent",
            parameter_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "ID of the agent"},
                    "limit": {"type": "integer", "description": "Maximum number of experiences to retrieve"}
                },
                "required": ["agent_id"]
            }
        )
        
        registry.register_function(
            func=self.get_experience_stats,
            name="get_experience_stats",
            description="Get statistics about the experience replay buffer",
            parameter_schema={
                "type": "object",
                "properties": {}
            }
        )
        
        registry.register_function(
            func=self.start_collaborative_training,
            name="start_collaborative_training",
            description="Start a collaborative training cycle",
            parameter_schema={
                "type": "object",
                "properties": {
                    "batch_size": {"type": "integer", "description": "Batch size for training"}
                }
            }
        )
        
        # Register additional workflows
        workflow_registry.register_workflow(
            name="collaborative_analysis",
            description="Execute a collaborative analysis using multiple agents",
            steps=[
                {
                    "function": "execute_agent_capability",
                    "parameters": {
                        "agent_id": "levy_analysis",
                        "capability": "analyze_tax_distribution"
                    }
                },
                {
                    "function": "execute_agent_capability",
                    "parameters": {
                        "agent_id": "levy_prediction",
                        "capability": "predict_levy_rates"
                    }
                },
                {
                    "function": "execute_agent_capability",
                    "parameters": {
                        "agent_id": "workflow_coordinator",
                        "capability": "execute_comprehensive_analysis"
                    }
                }
            ]
        )
        
        logger.info("Registered additional MCP Army functions and workflows")
        
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the current status of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Status dictionary
        """
        return agent_manager.get_agent_status(agent_id)
        
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Get a list of all registered agents with their status.
        
        Returns:
            List of agent information dictionaries
        """
        return agent_manager.list_agents()
        
    def execute_agent_capability(self, agent_id: str, capability: str, 
                               parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a capability on a specific agent.
        
        Args:
            agent_id: ID of the agent
            capability: Name of the capability to execute
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability execution
        """
        return agent_manager.execute_capability(agent_id, capability, parameters)
        
    def request_agent_assistance(self, agent_id: str, target_agent: str, 
                               assistance_type: str = 'general') -> Dict[str, Any]:
        """
        Request one agent to assist another.
        
        Args:
            agent_id: ID of the agent providing assistance
            target_agent: ID of the agent needing assistance
            assistance_type: Type of assistance needed
            
        Returns:
            Result of the assistance request
        """
        return agent_manager.request_assistance(agent_id, target_agent, assistance_type)
        
    def get_agent_experiences(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get experiences from the replay buffer for an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of experiences to retrieve
            
        Returns:
            List of experiences
        """
        all_experiences = collaboration_manager.replay_buffer.get_all()
        agent_experiences = [
            exp for exp in all_experiences
            if exp.get('agentId') == agent_id
        ]
        return agent_experiences[-limit:] if agent_experiences else []
        
    def get_experience_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the experience replay buffer.
        
        Returns:
            Statistics dictionary
        """
        all_experiences = collaboration_manager.replay_buffer.get_all()
        
        # Count experiences by agent
        agent_counts = {}
        for exp in all_experiences:
            agent_id = exp.get('agentId')
            if agent_id:
                agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
                
        # Count experiences by type
        type_counts = {}
        for exp in all_experiences:
            event_type = exp.get('eventType')
            if event_type:
                type_counts[event_type] = type_counts.get(event_type, 0) + 1
                
        return {
            'total_experiences': len(all_experiences),
            'by_agent': agent_counts,
            'by_type': type_counts
        }
        
    def start_collaborative_training(self, batch_size: int = 32) -> Dict[str, Any]:
        """
        Start a collaborative training cycle.
        
        Args:
            batch_size: Batch size for training
            
        Returns:
            Training result
        """
        training_started = collaboration_manager.start_training_cycle(batch_size)
        
        if training_started:
            return {
                'status': 'training_started',
                'batch_size': batch_size
            }
        else:
            return {
                'status': 'training_already_in_progress'
            }
            
    def shutdown(self) -> None:
        """Shutdown the integration system."""
        if self.initialized:
            # Stop agent monitoring
            agent_manager.stop_monitoring()
            self.initialized = False
            logger.info("MCP Army integration shutdown complete")


# Create the global integration instance
mcp_army_integration = MCPArmyIntegration()