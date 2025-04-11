"""
Error handling utilities for the Levy Calculation System.

This module provides a comprehensive error handling framework including:
- Custom exception hierarchy
- Error logging utilities
- Error response formatting
- Exception wrapping for consistent handling
"""

import logging
import traceback
import functools
import json
from typing import Dict, Any, Callable, Type, Optional, Union
from datetime import datetime

from flask import current_app, jsonify, Response, request

# Configure logging
logger = logging.getLogger(__name__)

# Custom Exception Classes
class LevySystemException(Exception):
    """Base class for all Levy System exceptions."""
    
    def __init__(self, message: str = None, error_code: str = None, 
                 status_code: int = 500, details: Dict[str, Any] = None):
        """
        Initialize a LevySystemException.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for clients
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message or "An error occurred in the Levy Calculation System"
        self.error_code = error_code or "SYSTEM_ERROR"
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        
        super().__init__(self.message)
        

class ValidationError(LevySystemException):
    """Exception raised for input validation errors."""
    
    def __init__(self, message: str = None, field: str = None, 
                 details: Dict[str, Any] = None):
        """
        Initialize a ValidationError.
        
        Args:
            message: Human-readable error message
            field: The field that failed validation
            details: Additional error details
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
            
        super().__init__(
            message=message or "Validation error",
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=error_details
        )


class DataAccessError(LevySystemException):
    """Exception raised for database access errors."""
    
    def __init__(self, message: str = None, entity: str = None, 
                 operation: str = None, details: Dict[str, Any] = None):
        """
        Initialize a DataAccessError.
        
        Args:
            message: Human-readable error message
            entity: The entity being accessed (table, collection)
            operation: The operation that failed (read, write, delete)
            details: Additional error details
        """
        error_details = details or {}
        if entity:
            error_details["entity"] = entity
        if operation:
            error_details["operation"] = operation
            
        super().__init__(
            message=message or "Database access error",
            error_code="DATA_ACCESS_ERROR",
            status_code=500,
            details=error_details
        )


class ApiError(LevySystemException):
    """Exception raised for API access errors."""
    
    def __init__(self, message: str = None, service: str = None, 
                 endpoint: str = None, status_code: int = None, 
                 details: Dict[str, Any] = None):
        """
        Initialize an ApiError.
        
        Args:
            message: Human-readable error message
            service: The API service that failed
            endpoint: The specific endpoint that failed
            status_code: The HTTP status code returned by the API
            details: Additional error details
        """
        error_details = details or {}
        if service:
            error_details["service"] = service
        if endpoint:
            error_details["endpoint"] = endpoint
        if status_code:
            error_details["status_code"] = status_code
            
        super().__init__(
            message=message or "API access error",
            error_code="API_ERROR",
            status_code=502,  # Bad Gateway
            details=error_details
        )


class NotFoundError(LevySystemException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, message: str = None, resource_type: str = None, 
                 resource_id: Any = None, details: Dict[str, Any] = None):
        """
        Initialize a NotFoundError.
        
        Args:
            message: Human-readable error message
            resource_type: The type of resource not found
            resource_id: The ID of the resource not found
            details: Additional error details
        """
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
            
        super().__init__(
            message=message or "Resource not found",
            error_code="NOT_FOUND",
            status_code=404,
            details=error_details
        )


class AuthorizationError(LevySystemException):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str = None, required_role: str = None, 
                 details: Dict[str, Any] = None):
        """
        Initialize an AuthorizationError.
        
        Args:
            message: Human-readable error message
            required_role: The role required for access
            details: Additional error details
        """
        error_details = details or {}
        if required_role:
            error_details["required_role"] = required_role
            
        super().__init__(
            message=message or "Not authorized to perform this action",
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=error_details
        )


# Error handling utilities
def log_exception(exception: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log an exception with context information.
    
    Args:
        exception: The exception to log
        context: Additional context information
    """
    context = context or {}
    
    # Add request info if available
    if request:
        context.update({
            "url": request.url,
            "method": request.method,
            "remote_addr": request.remote_addr
        })
    
    # Generate traceback
    tb = traceback.format_exc()
    
    # Log with appropriate level based on exception type
    if isinstance(exception, (ValidationError, NotFoundError)):
        logger.warning(
            f"Client error: {str(exception)}",
            extra={"context": context, "traceback": tb}
        )
    elif isinstance(exception, AuthorizationError):
        logger.error(
            f"Authorization error: {str(exception)}",
            extra={"context": context, "traceback": tb}
        )
    else:
        logger.error(
            f"System error: {str(exception)}",
            extra={"context": context, "traceback": tb}
        )


def format_error_response(exception: Exception) -> Dict[str, Any]:
    """
    Format an exception into a standardized error response.
    
    Args:
        exception: The exception to format
        
    Returns:
        A dictionary with formatted error information
    """
    if isinstance(exception, LevySystemException):
        response = {
            "success": False,
            "error": {
                "code": exception.error_code,
                "message": exception.message,
                "details": exception.details,
                "timestamp": exception.timestamp.isoformat()
            }
        }
    else:
        # Generic error for non-system exceptions
        response = {
            "success": False,
            "error": {
                "code": "UNEXPECTED_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Add original error message in development
        if current_app.config.get("DEBUG", False):
            response["error"]["details"] = {
                "exception_type": exception.__class__.__name__,
                "exception_message": str(exception),
                "traceback": traceback.format_exc().split("\n")
            }
    
    return response


def handle_exception(exception: Exception) -> Response:
    """
    Handle an exception and return an appropriate HTTP response.
    
    Args:
        exception: The exception to handle
        
    Returns:
        A Flask Response object
    """
    # Log the exception
    log_exception(exception)
    
    # Format the error response
    response_data = format_error_response(exception)
    
    # Determine status code
    if isinstance(exception, LevySystemException):
        status_code = exception.status_code
    else:
        status_code = 500
    
    # Return JSON response
    return jsonify(response_data), status_code


def exception_handler(exception_class: Type[Exception] = Exception):
    """
    Decorator for route handlers to catch and handle exceptions.
    
    Args:
        exception_class: The exception class to catch (default: Exception)
        
    Returns:
        A decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_class as e:
                return handle_exception(e)
        return wrapper
    return decorator


# Utility functions for common error checking
def check_required_fields(data: Dict[str, Any], required_fields: list, 
                          entity_name: str = "request") -> None:
    """
    Check that required fields are present in the provided data.
    
    Args:
        data: The data to check
        required_fields: List of field names that are required
        entity_name: Name of the entity being validated
        
    Raises:
        ValidationError: If any required fields are missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValidationError(
            message=f"Missing required fields for {entity_name}",
            details={"missing_fields": missing_fields}
        )


def check_resource_exists(resource, resource_type: str, resource_id: Any) -> None:
    """
    Check that a resource exists.
    
    Args:
        resource: The resource to check (can be None if not found)
        resource_type: The type of resource
        resource_id: The ID of the resource
        
    Raises:
        NotFoundError: If the resource is None
    """
    if resource is None:
        raise NotFoundError(
            message=f"{resource_type} with ID {resource_id} not found",
            resource_type=resource_type,
            resource_id=resource_id
        )