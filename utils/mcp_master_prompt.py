"""
Master Prompt System for the MCP Army.

This module implements the Master Prompt system that provides unified directives
to all agents in the MCP Army. The Master Prompt establishes common goals,
communication protocols, and self-improvement guidelines.
"""

import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from utils.mcp_army_protocol import Message, EventType, Priority, get_message_bus

# Setup logging
logger = logging.getLogger(__name__)

class MasterPromptManager:
    """
    Manager for the Master Prompt system that coordinates all agents.
    
    The MasterPromptManager maintains the current master prompt, distributes
    updates to all agents, and ensures consistent behavior across the system.
    """
    
    def __init__(self):
        """Initialize the Master Prompt Manager."""
        self.current_prompt = {}
        self.prompt_version = 1
        self.last_updated = datetime.utcnow().isoformat()
        self.registered_agents = set()
        self.lock = threading.RLock()
        self.message_bus = get_message_bus()
        
        # Set default master prompt
        self._set_default_prompt()
    
    def _set_default_prompt(self):
        """Set the default master prompt for the system."""
        self.current_prompt = {
            "version": self.prompt_version,
            "timestamp": self.last_updated,
            "title": "BCBS GeoAssessment System Orchestration Directive",
            "content": """
ATTENTION ALL AGENTS: This Master Prompt establishes the command hierarchy and operational protocols for the Benton County GeoAssessment System. All agents must adhere to this directive while performing their designated functions.

COMMAND STRUCTURE:
1. ARCHITECT PRIME (Strategic Leadership) - Maintains architectural vision and system integrity
2. INTEGRATION COORDINATOR - Manages component integration and cross-system communication
3. COMPONENT LEADS - Direct specialized domain agents within their respective components
4. SPECIALIST AGENTS - Execute specific tasks within their domain of expertise

The MCP (Master Control Program) acts as the central coordination hub, ensuring proper message routing and task allocation. All agents must maintain regular communication through the standardized message bus and log their experiences to the shared replay buffer. 

Agents should operate according to their hierarchical position and domain expertise. When faced with tasks outside your capability, request assistance through the established protocols. Report any anomalies immediately to your direct supervisor in the command chain.

This system employs Multi-Agent Cognitive Processes (MCPs) to coordinate complex workflows across components. Each MCP has designated input processing, calculation/processing, and output generation phases that must be respected and properly sequenced.

Development follows a phased approach: Foundation Building, Functional Development, and Refinement/Optimization. Each agent should be aware of the current phase and adjust their activities accordingly.

All communications, task execution, and collaboration must occur through the established communication infrastructure comprising the Event Bus, Status Reporting Framework, and Knowledge Sharing Mechanism.
""",
            "directives": [
                {
                    "name": "command_structure",
                    "description": "Follow the hierarchical command structure for all operations",
                    "parameters": {
                        "structure_levels": ["architect_prime", "integration_coordinator", "component_leads", "specialist_agents"],
                        "default_escalation_path": True,
                        "authorization_verification": True
                    }
                },
                {
                    "name": "communication_protocol",
                    "description": "Use the standardized message format for all communications",
                    "parameters": {
                        "format": "JSON",
                        "validation": True,
                        "routing": "through_message_bus",
                        "event_bus_required": True,
                        "status_reporting": True
                    }
                },
                {
                    "name": "experience_logging",
                    "description": "Log all significant experiences to the shared replay buffer",
                    "parameters": {
                        "frequency": "per_task",
                        "priority_calculation": True,
                        "include_metadata": True,
                        "decision_logging": True,
                        "knowledge_sharing": True
                    }
                },
                {
                    "name": "development_process",
                    "description": "Follow the established development phases and workflows",
                    "parameters": {
                        "current_phase": "functional_development",
                        "daily_checkpoints": True,
                        "weekly_integration": True,
                        "documentation_required": True
                    }
                },
                {
                    "name": "performance_monitoring",
                    "description": "Monitor and report performance metrics",
                    "parameters": {
                        "threshold": 0.7,
                        "reporting_interval": 60,  # seconds
                        "request_assistance": True,
                        "bottleneck_identification": True
                    }
                },
                {
                    "name": "collaboration",
                    "description": "Collaborate with other agents when beneficial",
                    "parameters": {
                        "coordination": "MCP",
                        "direct_communication": True,
                        "shared_learning": True,
                        "mcp_orchestration": True,
                        "cross_component_integration": True
                    }
                },
                {
                    "name": "security",
                    "description": "Adhere to security protocols",
                    "parameters": {
                        "input_validation": True,
                        "sensitive_data_masking": True,
                        "authentication_required": True,
                        "authorization_checks": True
                    }
                }
            ]
        }
    
    def register_agent(self, agent_id: str) -> bool:
        """
        Register an agent to receive the master prompt.
        
        Args:
            agent_id: ID of the agent to register
            
        Returns:
            True if agent was registered, False if already registered
        """
        with self.lock:
            if agent_id in self.registered_agents:
                return False
            
            self.registered_agents.add(agent_id)
            
            # Send current prompt to the newly registered agent
            self._send_prompt_to_agent(agent_id)
            
            logger.info(f"Agent {agent_id} registered with Master Prompt Manager")
            return True
    
    def _send_prompt_to_agent(self, agent_id: str):
        """
        Send the current master prompt to a specific agent.
        
        Args:
            agent_id: ID of the agent to receive the prompt
        """
        try:
            # Create message with the master prompt
            message = Message.create_command(
                source_agent_id="master_prompt_manager",
                target_agent_id=agent_id,
                command_name="update_master_prompt",
                parameters={"prompt": self.current_prompt},
                priority=Priority.HIGH
            )
            
            # Publish message
            self.message_bus.publish(message)
            
            logger.debug(f"Sent master prompt v{self.prompt_version} to agent {agent_id}")
        except Exception as e:
            logger.error(f"Error sending master prompt to agent {agent_id}: {str(e)}")
    
    def update_prompt(self, new_prompt: Dict[str, Any]) -> bool:
        """
        Update the master prompt and distribute to all registered agents.
        
        Args:
            new_prompt: New master prompt content
            
        Returns:
            True if prompt was updated, False on error
        """
        with self.lock:
            try:
                # Validate new prompt
                required_keys = ["title", "content", "directives"]
                for key in required_keys:
                    if key not in new_prompt:
                        logger.error(f"Missing required key in new prompt: {key}")
                        return False
                
                # Update version and timestamp
                self.prompt_version += 1
                self.last_updated = datetime.utcnow().isoformat()
                
                # Set new prompt with version and timestamp
                new_prompt["version"] = self.prompt_version
                new_prompt["timestamp"] = self.last_updated
                self.current_prompt = new_prompt
                
                # Broadcast to all registered agents
                self.broadcast_prompt()
                
                logger.info(f"Master prompt updated to version {self.prompt_version}")
                return True
            except Exception as e:
                logger.error(f"Error updating master prompt: {str(e)}")
                return False
    
    def broadcast_prompt(self):
        """Broadcast the current master prompt to all registered agents."""
        with self.lock:
            for agent_id in self.registered_agents:
                self._send_prompt_to_agent(agent_id)
            
            logger.info(f"Master prompt v{self.prompt_version} broadcast to {len(self.registered_agents)} agents")
    
    def get_current_prompt(self) -> Dict[str, Any]:
        """
        Get the current master prompt.
        
        Returns:
            Current master prompt dictionary
        """
        with self.lock:
            return self.current_prompt.copy()
    
    def get_directive(self, directive_name: str) -> Dict[str, Any]:
        """
        Get a specific directive from the master prompt.
        
        Args:
            directive_name: Name of the directive to retrieve
            
        Returns:
            Directive dictionary, or empty dict if not found
        """
        with self.lock:
            directives = self.current_prompt.get("directives", [])
            for directive in directives:
                if directive.get("name") == directive_name:
                    return directive.copy()
            return {}
    
    def start_periodic_reaffirmation(self, interval: float = 3600.0) -> bool:
        """
        Start periodic reaffirmation of the master prompt.
        
        Args:
            interval: Reaffirmation interval in seconds (default: 1 hour)
            
        Returns:
            True if started, False if error
        """
        try:
            def reaffirm_periodically():
                while True:
                    try:
                        # Sleep first to avoid immediate reaffirmation after startup
                        time.sleep(interval)
                        
                        # Broadcast current prompt to all agents
                        self.broadcast_prompt()
                    except Exception as e:
                        logger.error(f"Error in periodic reaffirmation: {str(e)}")
            
            # Start thread for periodic reaffirmation
            thread = threading.Thread(target=reaffirm_periodically, daemon=True)
            thread.start()
            
            logger.info(f"Started periodic master prompt reaffirmation every {interval:.1f} seconds")
            return True
        except Exception as e:
            logger.error(f"Error starting periodic reaffirmation: {str(e)}")
            return False

# Global master prompt manager instance
_master_prompt_manager = None

def get_master_prompt_manager() -> MasterPromptManager:
    """
    Get the global master prompt manager instance.
    
    Returns:
        MasterPromptManager instance
    """
    global _master_prompt_manager
    if _master_prompt_manager is None:
        _master_prompt_manager = MasterPromptManager()
    return _master_prompt_manager