"""
MCP Experience Replay Buffer and Agent Communication System.

This module implements a shared replay buffer and communication system for MCP agents,
facilitating experience sharing, collaborative learning, and dynamic assistance.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Deque
from collections import deque
import threading
import random

from utils.mcp_army_protocol import Message, get_message_bus, EventType, Priority

logger = logging.getLogger(__name__)

class ExperienceReplayBuffer:
    """
    A buffer for storing and retrieving agent experiences.
    
    This buffer enables agents to share experiences, learn from each other,
    and collectively improve their performance over time. It implements
    a prioritized experience replay mechanism where important experiences
    are more likely to be sampled for training.
    """
    
    def __init__(self, max_size: int = 10000, alpha: float = 0.6, beta: float = 0.4):
        """
        Initialize the experience replay buffer.
        
        Args:
            max_size: Maximum number of experiences to store
            alpha: Priority exponent (higher values increase priority impact)
            beta: Importance sampling exponent (higher values reduce importance sampling bias)
        """
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        self.priorities = deque(maxlen=max_size)
        self.alpha = alpha
        self.beta = beta
        self.lock = threading.RLock()
        
    def add(self, experience: Dict[str, Any], priority: float = 1.0) -> None:
        """
        Add an experience to the buffer with the given priority.
        
        Args:
            experience: The experience to add
            priority: Initial priority value (default: 1.0)
        """
        with self.lock:
            experience['timestamp'] = datetime.utcnow().isoformat()
            self.buffer.append(experience)
            self.priorities.append(priority ** self.alpha)
            
    def sample(self, batch_size: int = 32) -> List[Dict[str, Any]]:
        """
        Sample experiences from the buffer based on their priorities.
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            List of sampled experiences
        """
        with self.lock:
            if not self.buffer:
                return []
                
            # Ensure batch_size doesn't exceed buffer size
            actual_batch_size = min(batch_size, len(self.buffer))
            
            # Convert priorities to probabilities
            total_priority = sum(self.priorities)
            probabilities = [p / total_priority for p in self.priorities]
            
            # Sample experiences based on priorities
            indices = random.choices(
                range(len(self.buffer)), 
                weights=probabilities, 
                k=actual_batch_size
            )
            
            # Return sampled experiences
            return [self.buffer[i] for i in indices]
    
    def update_priority(self, experience_id: str, new_priority: float) -> bool:
        """
        Update the priority of a specific experience.
        
        Args:
            experience_id: Unique identifier of the experience
            new_priority: New priority value
            
        Returns:
            True if the experience was found and updated, False otherwise
        """
        with self.lock:
            for i, exp in enumerate(self.buffer):
                if exp.get('id') == experience_id:
                    self.priorities[i] = new_priority ** self.alpha
                    return True
            return False
    
    def size(self) -> int:
        """
        Get the current size of the buffer.
        
        Returns:
            Number of experiences in the buffer
        """
        with self.lock:
            return len(self.buffer)
    
    def clear(self) -> None:
        """Clear all experiences from the buffer."""
        with self.lock:
            self.buffer.clear()
            self.priorities.clear()
            
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all experiences in the buffer.
        
        Returns:
            List of all experiences
        """
        with self.lock:
            return list(self.buffer)
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save the buffer contents to a file.
        
        Args:
            filepath: Path to the output file
        """
        with self.lock:
            with open(filepath, 'w') as f:
                json.dump(list(self.buffer), f, indent=2)
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load buffer contents from a file.
        
        Args:
            filepath: Path to the input file
        """
        with self.lock:
            try:
                with open(filepath, 'r') as f:
                    experiences = json.load(f)
                    self.buffer.clear()
                    self.priorities.clear()
                    for exp in experiences:
                        self.buffer.append(exp)
                        self.priorities.append(1.0 ** self.alpha)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Error loading experiences from {filepath}: {str(e)}")


class AgentCommunicationBus:
    """
    Communication bus for agent messaging and coordination.
    
    This class facilitates standardized communication between agents,
    enabling message passing, event broadcasting, and coordination.
    """
    
    def __init__(self):
        """Initialize the agent communication bus."""
        self.subscribers = {}  # event_type -> list of callbacks
        self.message_history = []
        self.lock = threading.RLock()
        
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(callback)
            
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Unsubscribe from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to remove
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        with self.lock:
            if event_type in self.subscribers and callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
                return True
            return False
            
    def publish(self, message: Dict[str, Any]) -> None:
        """
        Publish a message to all subscribers of its event type.
        
        Args:
            message: Message to publish (must contain 'eventType')
        """
        event_type = message.get('eventType')
        if not event_type:
            logger.error("Cannot publish message without eventType")
            return
            
        with self.lock:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.utcnow().isoformat()
                
            # Store message in history
            self.message_history.append(message)
            
            # Limit history size
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-1000:]
                
            # Notify subscribers
            if event_type in self.subscribers:
                for callback in self.subscribers[event_type]:
                    try:
                        callback(message)
                    except Exception as e:
                        logger.error(f"Error in subscriber callback: {str(e)}")
                        
    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get message history, optionally filtered by event type.
        
        Args:
            event_type: Event type to filter by (optional)
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        with self.lock:
            if event_type:
                filtered = [m for m in self.message_history if m.get('eventType') == event_type]
                return filtered[-limit:] if filtered else []
            else:
                return self.message_history[-limit:] if self.message_history else []
                

class MCPCollaborationManager:
    """
    Manages collaboration between MCP agents.
    
    This class coordinates agent interactions, experience sharing,
    and collaborative learning. It serves as the central hub for
    the MCP agent collaboration framework.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP collaboration manager.
        
        Args:
            config: Configuration parameters (optional)
        """
        self.config = config if config is not None else {}
        self.replay_buffer = ExperienceReplayBuffer(
            max_size=self.config.get('replay_buffer_size', 10000),
            alpha=self.config.get('priority_alpha', 0.6),
            beta=self.config.get('priority_beta', 0.4)
        )
        self.comms_bus = AgentCommunicationBus()
        self.agents = {}  # agent_id -> agent instance
        self.performance_metrics = {}  # agent_id -> metrics dict
        self.training_lock = threading.Lock()
        self.is_training = False
        
    def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Register an agent with the collaboration manager.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance
        """
        self.agents[agent_id] = agent
        
        # Subscribe to agent events
        def handle_agent_event(message):
            # Add to experience replay if it's an action or result
            if message.get('eventType') in ['action', 'result']:
                self.replay_buffer.add(message)
                
            # Update performance metrics if it's a status update
            if message.get('eventType') == 'status_update':
                agent_id = message.get('agentId')
                if agent_id and 'performance' in message.get('payload', {}):
                    self.performance_metrics[agent_id] = message['payload']['performance']
                    
        self.comms_bus.subscribe('action', handle_agent_event)
        self.comms_bus.subscribe('result', handle_agent_event)
        self.comms_bus.subscribe('status_update', handle_agent_event)
        
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the collaboration manager.
        
        Args:
            agent_id: Agent ID to unregister
            
        Returns:
            True if successfully unregistered, False otherwise
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False
        
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
        
    def list_agents(self) -> List[str]:
        """
        Get list of all registered agent IDs.
        
        Returns:
            List of agent IDs
        """
        return list(self.agents.keys())
        
    def request_help(self, requesting_agent_id: str, task: str, priority_level: Priority = Priority.MEDIUM) -> None:
        """
        Request help from other agents for a specific task.
        
        Args:
            requesting_agent_id: ID of the agent requesting help
            task: Description of the task needing help
            priority_level: Priority of the help request
        """
        # Create a standardized assistance request message
        message = Message.create_assistance_request(
            source_agent_id=requesting_agent_id,
            assistance_type="task",
            assistance_reason=task,
            urgency=priority_level,
            target_agent_id="MCP"  # Send to MCP for routing to appropriate agent
        )
        
        # Publish via the message bus
        message_bus = get_message_bus()
        message_bus.publish(message)
        
        # Also log to local comms bus for backwards compatibility
        help_message = {
            'agentId': requesting_agent_id,
            'eventType': 'help_request',
            'timestamp': datetime.utcnow().isoformat(),
            'payload': {
                'task': task,
                'priority': priority_level
            }
        }
        self.comms_bus.publish(help_message)
        
    def start_training_cycle(self, batch_size: int = 32) -> bool:
        """
        Start a training cycle using the experience replay buffer.
        
        Args:
            batch_size: Number of experiences to sample for training
            
        Returns:
            True if training started, False if already in progress
        """
        if self.training_lock.acquire(blocking=False):
            try:
                if self.is_training:
                    return False
                    
                self.is_training = True
                
                # Sample experiences for training
                experiences = self.replay_buffer.sample(batch_size)
                
                if experiences:
                    # Notify agents of training start
                    training_start_msg = {
                        'agentId': 'collaboration_manager',
                        'eventType': 'training_start',
                        'timestamp': datetime.utcnow().isoformat(),
                        'payload': {
                            'batch_size': len(experiences)
                        }
                    }
                    self.comms_bus.publish(training_start_msg)
                    
                    # TODO: Actual training logic would go here
                    # This would involve updating agent policies based on experiences
                    
                    # Notify agents of training completion
                    training_complete_msg = {
                        'agentId': 'collaboration_manager',
                        'eventType': 'training_complete',
                        'timestamp': datetime.utcnow().isoformat(),
                        'payload': {
                            'batch_size': len(experiences)
                        }
                    }
                    self.comms_bus.publish(training_complete_msg)
                
                return True
            finally:
                self.is_training = False
                self.training_lock.release()
        else:
            return False
            
    def check_performance_and_request_help(self, threshold: float = 0.7) -> List[str]:
        """
        Check agent performance and request help for underperforming agents.
        
        Args:
            threshold: Performance threshold below which help is requested
            
        Returns:
            List of agent IDs for which help was requested
        """
        help_requested = []
        
        for agent_id, metrics in self.performance_metrics.items():
            performance = metrics.get('overall', 0.0)
            if performance < threshold:
                # Convert performance score to priority level
                if performance < 0.3:
                    priority_level = Priority.HIGH
                elif performance < 0.5:
                    priority_level = Priority.MEDIUM
                else:
                    priority_level = Priority.LOW
                    
                self.request_help(
                    agent_id,
                    f"Agent {agent_id} is underperforming (score: {performance})",
                    priority_level=priority_level
                )
                help_requested.append(agent_id)
                
        return help_requested
        
    def get_experience_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the experience replay buffer.
        
        Returns:
            Dictionary with experience replay statistics
        """
        buffer_data = self.replay_buffer.get_all()
        total_experiences = len(buffer_data)
        
        # Count by agent
        agent_counts = {}
        for exp in buffer_data:
            agent_id = exp.get('agentId', 'unknown')
            agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
            
        # Count by event type
        event_counts = {}
        for exp in buffer_data:
            event_type = exp.get('eventType', 'unknown')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
        # Get most recent experiences timestamp
        most_recent = None
        if buffer_data:
            most_recent = max(
                [exp.get('timestamp', '2000-01-01T00:00:00') for exp in buffer_data]
            )
            
        return {
            'total_experiences': total_experiences,
            'by_agent': agent_counts,
            'by_event_type': event_counts,
            'most_recent': most_recent,
            'max_size': self.replay_buffer.max_size,
            'utilization': total_experiences / max(1, self.replay_buffer.max_size)
        }
        
    def get_agent_experiences(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get experiences for a specific agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of experiences to return
            
        Returns:
            List of experience dictionaries
        """
        buffer_data = self.replay_buffer.get_all()
        agent_experiences = [
            exp for exp in buffer_data
            if exp.get('agentId') == agent_id
        ]
        
        # Sort by timestamp (most recent first)
        agent_experiences.sort(
            key=lambda x: x.get('timestamp', '2000-01-01T00:00:00'),
            reverse=True
        )
        
        return agent_experiences[:limit]
        
    def get_agent_performance(self, agent_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Performance metrics dictionary, or empty dict if not found
        """
        return self.performance_metrics.get(agent_id, {})
        
    def update_agent_performance(self, agent_id: str, metrics: Dict[str, Any]) -> None:
        """
        Update performance metrics for an agent.
        
        Args:
            agent_id: ID of the agent
            metrics: Performance metrics to update
        """
        self.performance_metrics[agent_id] = metrics


# Initialize the global collaboration manager
collaboration_manager = MCPCollaborationManager()