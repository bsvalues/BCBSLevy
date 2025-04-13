"""
MCP Agent Manager for orchestrating the Agent Army.

This module implements the Agent Manager that coordinates the communication
and collaboration between AI agents in the system. It serves as the central
hub for agent registration, delegation, and monitoring.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable
import threading

from utils.mcp_core import registry
from utils.mcp_agents import MCPAgent
from utils.mcp_experience import collaboration_manager, AgentCommunicationBus
from typing import Any

# Define AgentNotAvailableError for better error handling
class AgentNotAvailableError(Exception):
    """Raised when a requested agent is not available."""
    pass

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manager for coordinating AI agents in the BCBS GeoAssessment system.
    
    The AgentManager serves as the central coordinator for the Agent Army,
    implementing the hierarchical command structure from the strategic guide.
    It handles agent registration, task delegation, performance monitoring,
    and system-wide coordination across all command levels.
    """
    
    def __init__(self, collab_manager=None):
        """
        Initialize the Agent Manager.
        
        Args:
            collab_manager: Optional collaboration manager instance. If None, uses global instance.
        """
        self.agents = {}  # agent_id -> agent instance
        self.agent_configs = {}  # agent_id -> configuration
        
        # Command structure hierarchy
        self.command_structure = {
            "architect_prime": None,  # Will store the agent instance
            "integration_coordinator": None,
            "component_leads": {},  # component_name -> agent_id
            "specialist_agents": {}  # domain -> [agent_ids]
        }
        
        # Track hierarchical relationships between agents
        self.agent_relationships = {}  # agent_id -> {"role": role, "reports_to": agent_id, "supervises": [agent_ids]}
        
        self.agent_statuses = {}  # agent_id -> status
        self.task_queue = []  # List of pending tasks
        self.comm_bus = AgentCommunicationBus()
        self.monitor_thread = None
        self.running = False
        self.lock = threading.RLock()
        
        # Use provided collaboration manager or global instance
        self.collaboration_manager = collab_manager if collab_manager is not None else collaboration_manager
        
        # Subscribe to relevant events
        self.comm_bus.subscribe('help_request', self._handle_help_request)
        self.comm_bus.subscribe('status_update', self._handle_status_update)
        self.comm_bus.subscribe('error', self._handle_error)
        
    def initialize_agent(self, agent_id: str, config: Dict[str, Any]) -> bool:
        """
        Initialize an agent with the given configuration.
        
        Args:
            agent_id: Unique identifier for the agent
            config: Configuration parameters for the agent
            
        Returns:
            True if agent was successfully initialized, False otherwise
        """
        with self.lock:
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already initialized")
                return False
                
            agent_type = config.get('type')
            if not agent_type:
                logger.error(f"Missing agent type in configuration for {agent_id}")
                return False
                
            try:
                # Create agent instance based on type
                if agent_type == 'MCP':
                    # Master Control Program special case
                    from utils.mcp_integration import init_mcp
                    init_mcp()
                    self.agents[agent_id] = 'MCP'
                elif agent_type == 'LevyAnalysisAgent':
                    from utils.mcp_agents import LevyAnalysisAgent
                    self.agents[agent_id] = LevyAnalysisAgent()
                elif agent_type == 'LevyPredictionAgent':
                    from utils.mcp_agents import LevyPredictionAgent
                    self.agents[agent_id] = LevyPredictionAgent()
                elif agent_type == 'WorkflowCoordinatorAgent':
                    from utils.mcp_agents import WorkflowCoordinatorAgent
                    self.agents[agent_id] = WorkflowCoordinatorAgent()
                else:
                    logger.error(f"Unknown agent type: {agent_type}")
                    return False
                    
                # Store configuration
                self.agent_configs[agent_id] = config
                
                # Set initial status
                self.agent_statuses[agent_id] = {
                    'status': 'active',  # Mark as active immediately so it appears in the dashboard
                    'last_updated': datetime.utcnow().isoformat(),
                    'performance': {
                        'overall': 1.0,  # Start with perfect score
                        'task_success_rate': 1.0,
                        'response_time': 0.0,
                        'error_rate': 0.0
                    }
                }
                
                # Register with collaboration manager
                if agent_id != 'MCP':  # MCP isn't a standard agent
                    self.collaboration_manager.register_agent(agent_id, self.agents[agent_id])
                
                logger.info(f"Agent {agent_id} ({agent_type}) initialized successfully")
                
                # Publish initialization event
                self.comm_bus.publish({
                    'agentId': agent_id,
                    'eventType': 'status_update',
                    'timestamp': datetime.utcnow().isoformat(),
                    'payload': {
                        'status': 'active',  # Match the status we set in the agent_statuses
                        'agent_type': agent_type
                    }
                })
                
                return True
                
            except Exception as e:
                logger.error(f"Error initializing agent {agent_id}: {str(e)}")
                return False
                
    def initialize_agent_army(self, config: Dict[str, Any] = None) -> bool:
        """
        Initialize the entire agent army based on configuration, following the hierarchical
        command structure from the strategic guide.
        
        Args:
            config: Army configuration (optional, uses default if None)
            
        Returns:
            True if all agents were successfully initialized, False otherwise
        """
        if config is None:
            # Default configuration for the agent army with command structure roles
            config = {
                'agents': [
                    {
                        'id': 'MCP',
                        'type': 'MCP',
                        'role': 'integration_coordinator',
                        'component': 'core',
                        'config': {}
                    },
                    {
                        'id': 'workflow_coordinator',
                        'type': 'WorkflowCoordinatorAgent',
                        'role': 'architect_prime',
                        'component': 'core',
                        'config': {}
                    },
                    {
                        'id': 'levy_analysis',
                        'type': 'LevyAnalysisAgent',
                        'role': 'component_lead',
                        'component': 'levy',
                        'config': {}
                    },
                    {
                        'id': 'levy_prediction',
                        'type': 'LevyPredictionAgent',
                        'role': 'specialist_agent',
                        'component': 'levy',
                        'domain': 'prediction',
                        'reports_to': 'levy_analysis',
                        'config': {}
                    }
                ]
            }
            
        success = True
        
        # First pass: Initialize all agents
        for agent_config in config.get('agents', []):
            agent_id = agent_config.get('id')
            if not agent_id:
                logger.error("Agent configuration missing 'id' field")
                success = False
                continue
                
            agent_success = self.initialize_agent(
                agent_id,
                {
                    'type': agent_config.get('type'),
                    'role': agent_config.get('role', 'specialist_agent'),
                    'component': agent_config.get('component', 'general'),
                    'domain': agent_config.get('domain', 'general'),
                    'reports_to': agent_config.get('reports_to'),
                    **(agent_config.get('config', {}))
                }
            )
            
            if not agent_success:
                success = False
                continue
                
            # Update command structure based on agent role
            role = agent_config.get('role')
            if role == 'architect_prime':
                self.command_structure['architect_prime'] = agent_id
            elif role == 'integration_coordinator':
                self.command_structure['integration_coordinator'] = agent_id
            elif role == 'component_lead':
                component = agent_config.get('component', 'general')
                self.command_structure['component_leads'][component] = agent_id
            elif role == 'specialist_agent':
                domain = agent_config.get('domain', 'general')
                if domain not in self.command_structure['specialist_agents']:
                    self.command_structure['specialist_agents'][domain] = []
                self.command_structure['specialist_agents'][domain].append(agent_id)
                
        # Second pass: Establish hierarchical relationships
        for agent_config in config.get('agents', []):
            agent_id = agent_config.get('id')
            if not agent_id or agent_id not in self.agents:
                continue
                
            role = agent_config.get('role', 'specialist_agent')
            reports_to = agent_config.get('reports_to')
            
            # If reports_to is not specified, determine based on role
            if not reports_to:
                if role == 'architect_prime':
                    reports_to = None  # Reports to no one
                elif role == 'integration_coordinator':
                    reports_to = self.command_structure['architect_prime']
                elif role == 'component_lead':
                    reports_to = self.command_structure['integration_coordinator']
                elif role == 'specialist_agent':
                    component = agent_config.get('component', 'general')
                    reports_to = self.command_structure['component_leads'].get(component)
                    
            # Initialize relationship data
            self.agent_relationships[agent_id] = {
                'role': role,
                'reports_to': reports_to,
                'supervises': []
            }
            
            # Update supervisor's relationship data
            if reports_to and reports_to in self.agent_relationships:
                if 'supervises' not in self.agent_relationships[reports_to]:
                    self.agent_relationships[reports_to]['supervises'] = []
                self.agent_relationships[reports_to]['supervises'].append(agent_id)
                
        # Log command structure
        logger.info(f"Agent Army initialized with command structure: {self.command_structure}")
        return success
        
    def delegate_task(self, agent_id: str, task: Dict[str, Any]) -> str:
        """
        Delegate a task to a specific agent.
        
        Args:
            agent_id: ID of the agent to handle the task
            task: Task parameters
            
        Returns:
            Task ID for tracking, or empty string on failure
        """
        with self.lock:
            if agent_id not in self.agents:
                logger.error(f"Cannot delegate task to unknown agent: {agent_id}")
                return ""
                
            task_id = str(uuid.uuid4())
            task_with_id = {
                'task_id': task_id,
                'agent_id': agent_id,
                **task
            }
            
            # Add to task queue
            self.task_queue.append(task_with_id)
            
            # Publish task delegation event
            self.comm_bus.publish({
                'agentId': 'agent_manager',
                'eventType': 'task_delegation',
                'timestamp': datetime.utcnow().isoformat(),
                'payload': {
                    'task_id': task_id,
                    'agent_id': agent_id,
                    'task_type': task.get('task_type', 'unknown')
                }
            })
            
            # Execute task if agent isn't MCP (MCP tasks are handled differently)
            if agent_id != 'MCP' and isinstance(self.agents[agent_id], MCPAgent):
                try:
                    start_time = time.time()
                    
                    # Handle the task based on its type
                    if task.get('task_type') == 'capability_execution':
                        capability = task.get('capability')
                        params = task.get('parameters', {})
                        
                        # Execute agent capability
                        result = self.agents[agent_id].handle_request(capability, params)
                        
                        execution_time = time.time() - start_time
                        
                        # Update agent performance metrics
                        self._update_agent_performance(agent_id, True, execution_time)
                        
                        # Publish task completion event
                        self.comm_bus.publish({
                            'agentId': agent_id,
                            'eventType': 'task_complete',
                            'timestamp': datetime.utcnow().isoformat(),
                            'payload': {
                                'task_id': task_id,
                                'execution_time': execution_time,
                                'result': result
                            }
                        })
                        
                    elif task.get('task_type') == 'assistance':
                        # Help another agent
                        target_agent = task.get('target_agent')
                        assistance_type = task.get('assistance_type', 'general')
                        
                        # Handle assistance based on type
                        # This is a placeholder - real implementation would depend on specific assistance types
                        logger.info(f"Agent {agent_id} assisting {target_agent} with {assistance_type}")
                        
                    else:
                        logger.warning(f"Unknown task type: {task.get('task_type')}")
                        
                except Exception as e:
                    logger.error(f"Error executing task {task_id}: {str(e)}")
                    
                    # Update agent performance metrics for failure
                    self._update_agent_performance(agent_id, False, time.time() - start_time)
                    
                    # Publish error event
                    self.comm_bus.publish({
                        'agentId': agent_id,
                        'eventType': 'error',
                        'timestamp': datetime.utcnow().isoformat(),
                        'payload': {
                            'task_id': task_id,
                            'error': str(e)
                        }
                    })
            
            return task_id
            
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the current status of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Status dictionary, or empty dict if agent not found
        """
        with self.lock:
            return self.agent_statuses.get(agent_id, {})
            
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Get a list of all registered agents with their status.
        
        Returns:
            List of agent information dictionaries
        """
        with self.lock:
            return [
                {
                    'id': agent_id,
                    'type': self.agent_configs.get(agent_id, {}).get('type', 'unknown'),
                    'status': self.agent_statuses.get(agent_id, {}).get('status', 'unknown'),
                    'performance': self.agent_statuses.get(agent_id, {}).get('performance', {})
                }
                for agent_id in self.agents.keys()
            ]
            
    def start_monitoring(self, interval: float = 60.0) -> bool:
        """
        Start the agent monitoring thread.
        
        Args:
            interval: Monitoring interval in seconds
            
        Returns:
            True if monitoring started, False if already running
        """
        with self.lock:
            if self.running:
                return False
                
            self.running = True
            
            def monitor_agents():
                while self.running:
                    try:
                        # Check for underperforming agents
                        for agent_id in self.agents:
                            if agent_id == 'MCP':
                                continue  # Skip MCP
                                
                            status = self.agent_statuses.get(agent_id, {})
                            performance = status.get('performance', {}).get('overall', 1.0)
                            
                            if performance < 0.7:  # Performance threshold
                                logger.warning(f"Agent {agent_id} is underperforming (score: {performance})")
                                
                                # Request assistance
                                self.collaboration_manager.request_help(
                                    agent_id,
                                    f"Agent {agent_id} is underperforming",
                                    priority=1.0 - performance
                                )
                                
                        # Process task queue
                        with self.lock:
                            # Remove completed tasks
                            self.task_queue = [t for t in self.task_queue 
                                              if t.get('status') != 'completed']
                                              
                    except Exception as e:
                        logger.error(f"Error in agent monitoring: {str(e)}")
                        
                    time.sleep(interval)
            
            self.monitor_thread = threading.Thread(target=monitor_agents, daemon=True)
            self.monitor_thread.start()
            
            logger.info(f"Agent monitoring started with interval {interval}s")
            return True
            
    def stop_monitoring(self) -> bool:
        """
        Stop the agent monitoring thread.
        
        Returns:
            True if monitoring was stopped, False if not running
        """
        with self.lock:
            if not self.running:
                return False
                
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2.0)
                self.monitor_thread = None
                
            logger.info("Agent monitoring stopped")
            return True
            
    def execute_capability(self, agent_id: str, capability: str, 
                          parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a capability on a specific agent.
        
        Args:
            agent_id: ID of the agent
            capability: Name of the capability to execute
            parameters: Parameters for the capability
            
        Returns:
            Result of the capability execution, or error information
        """
        with self.lock:
            if agent_id not in self.agents:
                return {'error': f"Unknown agent: {agent_id}"}
                
            if agent_id == 'MCP':
                # For MCP, execute function directly from registry
                try:
                    return registry.execute_function(capability, parameters or {})
                except Exception as e:
                    logger.error(f"Error executing MCP capability {capability}: {str(e)}")
                    return {'error': str(e)}
            else:
                # For other agents, delegate task
                task = {
                    'task_type': 'capability_execution',
                    'capability': capability,
                    'parameters': parameters or {}
                }
                
                task_id = self.delegate_task(agent_id, task)
                if not task_id:
                    return {'error': f"Failed to delegate task to agent {agent_id}"}
                    
                # In a real implementation, you might want to wait for the task to complete
                # and return the result. For now, we'll just return the task ID.
                return {'task_id': task_id, 'status': 'delegated'}
                
    def request_assistance(self, agent_id: str, target_agent: str, 
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
        with self.lock:
            if agent_id not in self.agents:
                return {'error': f"Unknown assisting agent: {agent_id}"}
                
            if target_agent not in self.agents:
                return {'error': f"Unknown target agent: {target_agent}"}
                
            task = {
                'task_type': 'assistance',
                'target_agent': target_agent,
                'assistance_type': assistance_type
            }
            
            task_id = self.delegate_task(agent_id, task)
            if not task_id:
                return {'error': f"Failed to delegate assistance task to agent {agent_id}"}
                
            return {'task_id': task_id, 'status': 'assistance_requested'}
            
    def update_all_agents(self, updated_policy: Dict[str, Any]) -> None:
        """
        Update all agents with a new policy.
        
        Args:
            updated_policy: New policy to apply to all agents
        """
        with self.lock:
            for agent_id, agent in self.agents.items():
                if agent_id == 'MCP':
                    continue  # Skip MCP
                    
                if hasattr(agent, 'update_policy'):
                    try:
                        agent.update_policy(updated_policy)
                    except Exception as e:
                        logger.error(f"Error updating policy for agent {agent_id}: {str(e)}")
                        
        # Publish policy update event
        self.comm_bus.publish({
            'agentId': 'agent_manager',
            'eventType': 'policy_update',
            'timestamp': datetime.utcnow().isoformat(),
            'payload': {
                'policy_version': updated_policy.get('version', 'unknown')
            }
        })
        
    def _handle_help_request(self, message: Dict[str, Any]) -> None:
        """
        Handle a help request event.
        
        Args:
            message: Help request message
        """
        agent_id = message.get('agentId')
        payload = message.get('payload', {})
        task = payload.get('task')
        priority = payload.get('priority', 1.0)
        
        if not agent_id or not task:
            logger.error("Invalid help request message")
            return
            
        logger.info(f"Help requested by agent {agent_id}: {task}")
        
        # Determine which agent is best suited to help
        # This is a simple implementation - in a real system, you would have more sophisticated logic
        helper_agent_id = None
        
        # For now, just use the workflow coordinator if available
        if 'workflow_coordinator' in self.agents:
            helper_agent_id = 'workflow_coordinator'
        else:
            # Otherwise, pick the first available agent that isn't the requesting agent
            for aid in self.agents:
                if aid != agent_id and aid != 'MCP':
                    helper_agent_id = aid
                    break
        
        if helper_agent_id:
            logger.info(f"Delegating help request to {helper_agent_id}")
            self.request_assistance(helper_agent_id, agent_id, 'help_request')
        else:
            logger.warning(f"No suitable agent found to help {agent_id}")
            
    def _handle_status_update(self, message: Dict[str, Any]) -> None:
        """
        Handle a status update event.
        
        Args:
            message: Status update message
        """
        agent_id = message.get('agentId')
        payload = message.get('payload', {})
        
        if not agent_id:
            return
            
        with self.lock:
            if agent_id in self.agent_statuses:
                # Update status fields
                current_status = self.agent_statuses[agent_id]
                
                # Update fields from payload
                for key, value in payload.items():
                    if key == 'performance' and isinstance(value, dict) and isinstance(current_status.get('performance'), dict):
                        # Merge performance metrics
                        current_status['performance'].update(value)
                    else:
                        # Direct update
                        current_status[key] = value
                        
                # Update timestamp
                current_status['last_updated'] = datetime.utcnow().isoformat()
                
    def _handle_error(self, message: Dict[str, Any]) -> None:
        """
        Handle an error event.
        
        Args:
            message: Error message
        """
        agent_id = message.get('agentId')
        payload = message.get('payload', {})
        error = payload.get('error')
        task_id = payload.get('task_id')
        
        if not agent_id or not error:
            return
            
        logger.error(f"Error from agent {agent_id}: {error}")
        
        # Update agent performance
        self._update_agent_performance(agent_id, False)
        
        # Check if assistance is needed
        with self.lock:
            status = self.agent_statuses.get(agent_id, {})
            performance = status.get('performance', {}).get('overall', 1.0)
            
            if performance < 0.7:  # Performance threshold
                self.collaboration_manager.request_help(
                    agent_id,
                    f"Agent {agent_id} encountered an error: {error}",
                    priority=1.0 - performance
                )
                
    def _update_agent_performance(self, agent_id: str, success: bool, 
                                 execution_time: float = 0.0) -> None:
        """
        Update an agent's performance metrics.
        
        Args:
            agent_id: ID of the agent
            success: Whether the task was successful
            execution_time: Task execution time in seconds
        """
        with self.lock:
            if agent_id not in self.agent_statuses:
                return
                
            status = self.agent_statuses[agent_id]
            if 'performance' not in status:
                status['performance'] = {
                    'overall': 1.0,
                    'task_success_rate': 1.0,
                    'response_time': 0.0,
                    'error_rate': 0.0,
                    'task_count': 0
                }
                
            perf = status['performance']
            
            # Update metrics
            perf['task_count'] = perf.get('task_count', 0) + 1
            success_count = perf.get('success_count', 0)
            
            if success:
                success_count += 1
                perf['success_count'] = success_count
                
            # Calculate success rate
            perf['task_success_rate'] = success_count / perf['task_count']
            
            # Update error rate
            perf['error_rate'] = 1.0 - perf['task_success_rate']
            
            # Update average response time
            avg_time = perf.get('response_time', 0.0)
            perf['response_time'] = (avg_time * (perf['task_count'] - 1) + execution_time) / perf['task_count']
            
            # Calculate overall performance (weighted average)
            perf['overall'] = (
                0.6 * perf['task_success_rate'] +
                0.3 * max(0, 1.0 - (perf['response_time'] / 2.0)) +  # Normalize response time
                0.1 * (1.0 - perf['error_rate'])
            )
            
            # Update collaboration manager
            self.collaboration_manager.update_agent_performance(agent_id, perf)


# Initialize the global agent manager
agent_manager = AgentManager()

# Function to get an agent by ID
def get_agent(agent_id: str) -> Any:
    """
    Get an agent by ID.
    
    This function serves as a wrapper around the collaboration manager's get_agent method
    for accessing agents from outside the MCP framework. It provides a standardized interface
    for retrieving agent instances throughout the application.
    
    Args:
        agent_id: The ID of the agent to retrieve
        
    Returns:
        The agent instance if found, None otherwise
        
    Raises:
        AgentNotAvailableError: If the agent is not available
    """
    try:
        # Check if collaboration manager is initialized
        if not collaboration_manager:
            logger.warning("Collaboration manager not initialized")
            return None
            
        # Retrieve the agent from the collaboration manager
        agent = collaboration_manager.get_agent(agent_id)
        if not agent:
            logger.warning(f"Agent {agent_id} not found")
            raise AgentNotAvailableError(f"Agent {agent_id} not available")
            
        return agent
    except Exception as e:
        logger.error(f"Error retrieving agent {agent_id}: {str(e)}")
        raise AgentNotAvailableError(f"Error retrieving agent {agent_id}: {str(e)}")