"""
Core Model Content Protocol (MCP) functionality and registry.

This module provides the foundation for the MCP framework, including:
- Function registration and discovery
- Protocol definition
- Core utilities
"""

import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union, TypeVar, Generic

logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')
FunctionType = Callable[..., Any]
ParameterType = Dict[str, Any]
ResultType = Dict[str, Any]


class MCPFunction:
    """Represents a registered MCP function."""
    
    def __init__(
        self,
        name: str,
        description: str,
        func: FunctionType,
        parameter_schema: Dict[str, Any] = None,
        return_schema: Dict[str, Any] = None
    ):
        """
        Initialize an MCP function.
        
        Args:
            name: Unique function identifier
            description: Human-readable function description
            func: The actual function implementation
            parameter_schema: JSON Schema for function parameters
            return_schema: JSON Schema for function return value
        """
        self.name = name
        self.description = description
        self.func = func
        self.parameter_schema = parameter_schema or {}
        self.return_schema = return_schema or {}
    
    def execute(self, parameters: ParameterType = None) -> ResultType:
        """
        Execute the function with the given parameters.
        
        Args:
            parameters: Function parameters
            
        Returns:
            Function result
        """
        parameters = parameters or {}
        try:
            result = self.func(**parameters)
            return result
        except Exception as e:
            logger.error(f"Error executing MCP function {self.name}: {str(e)}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the function to a dictionary representation.
        
        Returns:
            Dictionary with function metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameter_schema
        }


class MCPRegistry:
    """Registry for MCP functions and capabilities."""
    
    def __init__(self):
        """Initialize an empty registry."""
        self.functions: Dict[str, MCPFunction] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameter_schema: Dict[str, Any] = None,
        return_schema: Dict[str, Any] = None
    ) -> Callable[[FunctionType], FunctionType]:
        """
        Decorator to register a function with the MCP registry.
        
        Args:
            name: Unique function identifier
            description: Human-readable function description
            parameter_schema: JSON Schema for function parameters
            return_schema: JSON Schema for function return value
            
        Returns:
            Decorator function
        """
        def decorator(func: FunctionType) -> FunctionType:
            self.functions[name] = MCPFunction(
                name=name,
                description=description,
                func=func,
                parameter_schema=parameter_schema,
                return_schema=return_schema
            )
            return func
        return decorator
    
    def register_function(
        self,
        func: FunctionType,
        name: str = None,
        description: str = None,
        parameter_schema: Dict[str, Any] = None,
        return_schema: Dict[str, Any] = None
    ) -> None:
        """
        Register an existing function with the MCP registry.
        
        Args:
            func: The function to register
            name: Unique function identifier (defaults to function name)
            description: Human-readable function description
            parameter_schema: JSON Schema for function parameters
            return_schema: JSON Schema for function return value
        """
        name = name or func.__name__
        description = description or (func.__doc__ or "").strip()
        self.functions[name] = MCPFunction(
            name=name,
            description=description,
            func=func,
            parameter_schema=parameter_schema,
            return_schema=return_schema
        )
    
    def get_function(self, name: str) -> Optional[MCPFunction]:
        """
        Get a function by name.
        
        Args:
            name: Function name
            
        Returns:
            The MCPFunction or None if not found
        """
        return self.functions.get(name)
    
    def execute_function(self, name: str, parameters: ParameterType = None) -> ResultType:
        """
        Execute a function by name.
        
        Args:
            name: Function name
            parameters: Function parameters
            
        Returns:
            Function result
            
        Raises:
            ValueError: If the function is not found
        """
        function = self.get_function(name)
        if not function:
            raise ValueError(f"MCP function '{name}' not found")
        return function.execute(parameters)
    
    def has_function(self, name: str) -> bool:
        """
        Check if a function with the given name exists in the registry.
        
        Args:
            name: Function name to check
            
        Returns:
            True if the function exists, False otherwise
        """
        return name in self.functions
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """
        List all registered functions.
        
        Returns:
            List of function metadata dictionaries
        """
        return [func.to_dict() for func in self.functions.values()]


class MCPWorkflow:
    """Represents a sequence of MCP function calls."""
    
    def __init__(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        registry: MCPRegistry
    ):
        """
        Initialize an MCP workflow.
        
        Args:
            name: Unique workflow identifier
            description: Human-readable workflow description
            steps: List of workflow steps, each with a function name and parameters
            registry: The MCP registry to use for function lookup
        """
        self.name = name
        self.description = description
        self.steps = steps
        self.registry = registry
    
    def execute(self, initial_parameters: ParameterType = None) -> List[ResultType]:
        """
        Execute the workflow.
        
        Args:
            initial_parameters: Initial parameters for the workflow
            
        Returns:
            List of step results
        """
        parameters = initial_parameters or {}
        results = []
        
        for step in self.steps:
            function_name = step["function"]
            step_parameters = step.get("parameters", {})
            
            # Merge initial parameters with step parameters
            merged_parameters = {**parameters, **step_parameters}
            
            # Execute the function
            result = self.registry.execute_function(function_name, merged_parameters)
            results.append(result)
            
            # Update parameters with results for next step
            if isinstance(result, dict):
                parameters.update(result)
        
        return results
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary representation.
        
        Returns:
            Dictionary with workflow metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps
        }


class MCPWorkflowRegistry:
    """Registry for MCP workflows."""
    
    def __init__(self, function_registry: MCPRegistry):
        """
        Initialize a workflow registry.
        
        Args:
            function_registry: The MCP function registry to use
        """
        self.workflows: Dict[str, MCPWorkflow] = {}
        self.function_registry = function_registry
    
    def register(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> None:
        """
        Register a workflow.
        
        Args:
            name: Unique workflow identifier
            description: Human-readable workflow description
            steps: List of workflow steps, each with a function name and parameters
        """
        self.workflows[name] = MCPWorkflow(
            name=name,
            description=description,
            steps=steps,
            registry=self.function_registry
        )
    
    def get_workflow(self, name: str) -> Optional[MCPWorkflow]:
        """
        Get a workflow by name.
        
        Args:
            name: Workflow name
            
        Returns:
            The MCPWorkflow or None if not found
        """
        return self.workflows.get(name)
    
    def execute_workflow(self, name: str, parameters: ParameterType = None) -> List[ResultType]:
        """
        Execute a workflow by name.
        
        Args:
            name: Workflow name
            parameters: Initial parameters for the workflow
            
        Returns:
            List of step results
            
        Raises:
            ValueError: If the workflow is not found
        """
        workflow = self.get_workflow(name)
        if not workflow:
            raise ValueError(f"MCP workflow '{name}' not found")
        return workflow.execute(parameters)
    
    def has_workflow(self, name: str) -> bool:
        """
        Check if a workflow with the given name exists in the registry.
        
        Args:
            name: Workflow name to check
            
        Returns:
            True if the workflow exists, False otherwise
        """
        return name in self.workflows
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all registered workflows.
        
        Returns:
            List of workflow metadata dictionaries
        """
        return [workflow.to_dict() for workflow in self.workflows.values()]


# Create global registry instances
registry = MCPRegistry()
workflow_registry = MCPWorkflowRegistry(registry)


# Example function registrations
@registry.register(
    name="analyze_tax_distribution",
    description="Analyze distribution of tax burden across properties",
    parameter_schema={
        "type": "object",
        "properties": {
            "tax_code": {"type": "string", "description": "Tax code to analyze"}
        }
    }
)
def analyze_tax_distribution(tax_code: str = None) -> Dict[str, Any]:
    """
    Analyze distribution of tax burden across properties.
    
    Args:
        tax_code: Tax code to analyze (optional)
        
    Returns:
        Analysis results
    """
    # This is a placeholder - the actual implementation would analyze real data
    return {
        "analysis": "Tax distribution analysis complete",
        "distribution": {
            "median": 2500,
            "mean": 3200,
            "std_dev": 1500,
            "quartiles": [1500, 2500, 4500]
        },
        "insights": [
            "Properties in this tax code have a relatively even distribution",
            "No significant outliers detected"
        ]
    }


@registry.register(
    name="predict_levy_rates",
    description="Predict future levy rates based on historical data",
    parameter_schema={
        "type": "object",
        "properties": {
            "tax_code": {"type": "string", "description": "Tax code to predict"},
            "years": {"type": "integer", "description": "Number of years to predict"}
        }
    }
)
def predict_levy_rates(tax_code: str, years: int = 1) -> Dict[str, Any]:
    """
    Predict future levy rates based on historical data.
    
    Args:
        tax_code: Tax code to predict
        years: Number of years to predict
        
    Returns:
        Prediction results
    """
    # This is a placeholder - the actual implementation would analyze real data
    return {
        "predictions": {
            "year_1": 3.25,
            "year_2": 3.31 if years > 1 else None,
            "year_3": 3.37 if years > 2 else None
        },
        "confidence": 0.85,
        "factors": [
            "Historical growth trends",
            "Statutory limits",
            "Assessed value projections"
        ]
    }


# Register example workflows
workflow_registry.register(
    name="tax_distribution_analysis",
    description="Analyze tax distribution and generate insights",
    steps=[
        {
            "function": "analyze_tax_distribution",
            "parameters": {}
        },
        {
            "function": "predict_levy_rates",
            "parameters": {"years": 3}
        }
    ]
)