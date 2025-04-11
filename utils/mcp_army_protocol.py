"""
Standardized Communication Protocol & Message Format for the MCP Army.

This module defines the communication protocol used by all agents in the MCP Army
system, ensuring consistent message formatting, validation, and routing.
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, TypedDict

# Setup logging
logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Enumeration of message event types for the MCP Army communication protocol."""
    COMMAND = "COMMAND"  # Direct instruction to an agent
    EVENT = "EVENT"  # Notification of something that happened
    QUERY = "QUERY"  # Request for information
    RESPONSE = "RESPONSE"  # Reply to a query or command
    ERROR = "ERROR"  # Error notification
    STATUS_UPDATE = "STATUS_UPDATE"  # Agent reporting its status
    ASSISTANCE_REQUESTED = "ASSISTANCE_REQUESTED"  # Agent requesting help

class Priority(str, Enum):
    """Enumeration of message priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class MessageMetadata(TypedDict, total=False):
    """Type definition for message metadata."""
    priority: Priority
    ttl: int  # Time-to-live in seconds

class MessagePayload(TypedDict, total=False):
    """Type definition for message payload."""
    # Command-specific fields
    commandName: str
    dataRef: str
    parameters: Dict[str, Any]
    
    # Response-specific fields
    status: str
    result: Dict[str, Any]
    
    # Error-specific fields
    errorCode: str
    errorMessage: str
    stackTrace: str
    
    # Status update fields
    agentStatus: str
    performanceMetrics: Dict[str, Any]
    
    # Assistance fields
    assistanceType: str
    assistanceReason: str
    urgency: Priority

class Message:
    """
    Standard message format for communication between agents in the MCP Army.
    
    Provides methods for creating, validating, serializing, and deserializing messages
    according to the defined protocol.
    """
    
    def __init__(
        self,
        source_agent_id: str,
        target_agent_id: str,
        event_type: EventType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new message.
        
        Args:
            source_agent_id: ID of the agent sending the message
            target_agent_id: ID of the intended recipient (or 'broadcast')
            event_type: Type of message event
            payload: Event-specific data
            correlation_id: Optional ID to track a specific task or workflow
            message_id: Optional unique ID for this message (generated if not provided)
            timestamp: Optional timestamp (generated if not provided)
            metadata: Optional additional message metadata
        """
        self.message_id = message_id or str(uuid.uuid4())
        self.correlation_id = correlation_id or self.message_id
        self.source_agent_id = source_agent_id
        self.target_agent_id = target_agent_id
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.event_type = event_type
        self.payload = payload
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "messageId": self.message_id,
            "correlationId": self.correlation_id,
            "sourceAgentId": self.source_agent_id,
            "targetAgentId": self.target_agent_id,
            "timestamp": self.timestamp,
            "eventType": self.event_type,
            "payload": self.payload,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a Message object from a dictionary.
        
        Args:
            data: Dictionary representation of a message
            
        Returns:
            Message object
            
        Raises:
            ValueError: If the dictionary is missing required fields or has invalid format
        """
        # Validate required fields
        required_fields = [
            "messageId", "correlationId", "sourceAgentId", 
            "targetAgentId", "timestamp", "eventType", "payload"
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate event type
        try:
            event_type = EventType(data["eventType"])
        except ValueError:
            raise ValueError(f"Invalid event type: {data['eventType']}")
        
        return cls(
            message_id=data["messageId"],
            correlation_id=data["correlationId"],
            source_agent_id=data["sourceAgentId"],
            target_agent_id=data["targetAgentId"],
            timestamp=data["timestamp"],
            event_type=event_type,
            payload=data["payload"],
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """
        Create a Message object from a JSON string.
        
        Args:
            json_str: JSON string representation of a message
            
        Returns:
            Message object
            
        Raises:
            ValueError: If the JSON is invalid or missing required fields
            json.JSONDecodeError: If the JSON is malformed
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def create_command(
        cls,
        source_agent_id: str,
        target_agent_id: str,
        command_name: str,
        parameters: Dict[str, Any] = None,
        correlation_id: Optional[str] = None,
        priority: Priority = Priority.MEDIUM
    ) -> 'Message':
        """
        Create a command message.
        
        Args:
            source_agent_id: ID of the agent sending the command
            target_agent_id: ID of the agent that should execute the command
            command_name: Name of the command to execute
            parameters: Optional parameters for the command
            correlation_id: Optional ID to track a specific task or workflow
            priority: Message priority
            
        Returns:
            Message object with event type COMMAND
        """
        payload = {
            "commandName": command_name,
            "parameters": parameters or {}
        }
        
        metadata = {
            "priority": priority
        }
        
        return cls(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            event_type=EventType.COMMAND,
            payload=payload,
            correlation_id=correlation_id,
            metadata=metadata
        )
    
    @classmethod
    def create_response(
        cls,
        source_agent_id: str,
        target_agent_id: str,
        status: str,
        result: Dict[str, Any] = None,
        correlation_id: str = None,
        original_message_id: str = None
    ) -> 'Message':
        """
        Create a response message.
        
        Args:
            source_agent_id: ID of the agent sending the response
            target_agent_id: ID of the agent that should receive the response
            status: Status of the response ('success' or 'failure')
            result: Optional result data
            correlation_id: ID to track a specific task or workflow
            original_message_id: ID of the message this is responding to
            
        Returns:
            Message object with event type RESPONSE
        """
        payload = {
            "status": status,
            "result": result or {}
        }
        
        metadata = {}
        if original_message_id:
            metadata["inResponseTo"] = original_message_id
        
        return cls(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            event_type=EventType.RESPONSE,
            payload=payload,
            correlation_id=correlation_id,
            metadata=metadata
        )
    
    @classmethod
    def create_error(
        cls,
        source_agent_id: str,
        target_agent_id: str,
        error_code: str,
        error_message: str,
        stack_trace: str = None,
        correlation_id: str = None,
        original_message_id: str = None,
        priority: Priority = Priority.HIGH
    ) -> 'Message':
        """
        Create an error message.
        
        Args:
            source_agent_id: ID of the agent reporting the error
            target_agent_id: ID of the agent that should receive the error
            error_code: Error code
            error_message: Human-readable error message
            stack_trace: Optional stack trace
            correlation_id: ID to track a specific task or workflow
            original_message_id: ID of the message that caused the error
            priority: Message priority
            
        Returns:
            Message object with event type ERROR
        """
        payload = {
            "errorCode": error_code,
            "errorMessage": error_message
        }
        
        if stack_trace:
            payload["stackTrace"] = stack_trace
        
        metadata = {
            "priority": priority
        }
        
        if original_message_id:
            metadata["inResponseTo"] = original_message_id
        
        return cls(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            event_type=EventType.ERROR,
            payload=payload,
            correlation_id=correlation_id,
            metadata=metadata
        )
    
    @classmethod
    def create_status_update(
        cls,
        source_agent_id: str,
        agent_status: str,
        performance_metrics: Dict[str, Any] = None,
        target_agent_id: str = "MCP"
    ) -> 'Message':
        """
        Create a status update message.
        
        Args:
            source_agent_id: ID of the agent reporting its status
            agent_status: Status of the agent (e.g., 'active', 'idle', 'error')
            performance_metrics: Optional performance metrics
            target_agent_id: ID of the agent that should receive the status update
            
        Returns:
            Message object with event type STATUS_UPDATE
        """
        payload = {
            "agentStatus": agent_status,
            "performanceMetrics": performance_metrics or {}
        }
        
        return cls(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            event_type=EventType.STATUS_UPDATE,
            payload=payload
        )
    
    @classmethod
    def create_assistance_request(
        cls,
        source_agent_id: str,
        assistance_type: str,
        assistance_reason: str,
        urgency: Priority = Priority.MEDIUM,
        target_agent_id: str = "MCP"
    ) -> 'Message':
        """
        Create an assistance request message.
        
        Args:
            source_agent_id: ID of the agent requesting assistance
            assistance_type: Type of assistance needed
            assistance_reason: Reason for requesting assistance
            urgency: Urgency of the request
            target_agent_id: ID of the agent that should handle the assistance request
            
        Returns:
            Message object with event type ASSISTANCE_REQUESTED
        """
        payload = {
            "assistanceType": assistance_type,
            "assistanceReason": assistance_reason,
            "urgency": urgency
        }
        
        metadata = {
            "priority": urgency
        }
        
        return cls(
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            event_type=EventType.ASSISTANCE_REQUESTED,
            payload=payload,
            metadata=metadata
        )

# Message bus implementation (simplified for initial version)
class MessageBus:
    """
    Simple in-memory message bus implementation for agent communication.
    
    In a production environment, this would be replaced with a more robust
    solution like MQTT, Redis Pub/Sub, or a message queue system.
    """
    
    def __init__(self):
        """Initialize the message bus."""
        self.subscribers = {}
        self.message_history = []
        self.max_history = 1000
    
    def subscribe(self, agent_id: str, callback):
        """
        Subscribe an agent to receive messages.
        
        Args:
            agent_id: ID of the agent subscribing
            callback: Function to call when a message is received
        """
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        
        self.subscribers[agent_id].append(callback)
        logger.info(f"Agent {agent_id} subscribed to message bus")
    
    def unsubscribe(self, agent_id: str, callback=None):
        """
        Unsubscribe an agent from receiving messages.
        
        Args:
            agent_id: ID of the agent unsubscribing
            callback: Specific callback to unsubscribe, or None to unsubscribe all
        """
        if agent_id not in self.subscribers:
            return
        
        if callback is None:
            self.subscribers[agent_id] = []
            logger.info(f"Agent {agent_id} unsubscribed from all topics")
        else:
            self.subscribers[agent_id] = [
                cb for cb in self.subscribers[agent_id] if cb != callback
            ]
            logger.info(f"Agent {agent_id} unsubscribed specific callback")
    
    def publish(self, message: Message):
        """
        Publish a message to the bus.
        
        Args:
            message: Message to publish
        """
        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)
        
        # Determine recipients
        recipients = []
        
        if message.target_agent_id == "broadcast":
            # Send to all subscribers
            for agent_id, callbacks in self.subscribers.items():
                if agent_id != message.source_agent_id:  # Don't send to self
                    recipients.extend(callbacks)
        else:
            # Send to specific agent
            if message.target_agent_id in self.subscribers:
                recipients = self.subscribers[message.target_agent_id]
        
        # Deliver message
        for callback in recipients:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error delivering message to subscriber: {str(e)}")
        
        logger.debug(f"Published message: {message.message_id} from {message.source_agent_id} to {message.target_agent_id}")
    
    def get_history(self, limit: int = None, agent_id: str = None, event_type: EventType = None) -> List[Message]:
        """
        Get message history with optional filtering.
        
        Args:
            limit: Maximum number of messages to return
            agent_id: Filter by agent ID (source or target)
            event_type: Filter by event type
            
        Returns:
            List of messages matching the filters
        """
        filtered = self.message_history
        
        if agent_id:
            filtered = [
                msg for msg in filtered 
                if msg.source_agent_id == agent_id or msg.target_agent_id == agent_id
            ]
        
        if event_type:
            filtered = [
                msg for msg in filtered 
                if msg.event_type == event_type
            ]
        
        if limit:
            filtered = filtered[-limit:]
        
        return filtered

# Global message bus instance
_message_bus = None

def get_message_bus() -> MessageBus:
    """
    Get the global message bus instance.
    
    Returns:
        MessageBus instance
    """
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus