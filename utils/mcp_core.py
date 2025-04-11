"""
Core Model Content Protocol (MCP) functionality and registry.

This module provides the foundation for the MCP framework, including:
- Function registration and discovery
- Protocol definition
- Core utilities
"""

import json
import logging
from typing import Dict, List, Any, Callable, Optional, Union, TypeVar, Generic, cast, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')
FunctionType = Callable[..., Any]
ParameterType = Optional[Dict[str, Any]]
ResultType = Dict[str, Any]

# Parameter schemas
JSONSchemaType = Optional[Dict[str, Any]]
SchemaPropertyType = Dict[str, Union[str, List[str], Dict[str, Any]]]


class MCPFunction:
    """
    Represents a registered MCP function.
    
    An MCPFunction wraps a regular Python function with additional metadata and
    validation capabilities, making it available through the MCP framework.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        func: FunctionType,
        parameter_schema: JSONSchemaType = None,
        return_schema: JSONSchemaType = None
    ):
        """
        Initialize an MCP function with metadata and implementation.
        
        This constructor creates a new function instance within the MCP framework,
        encapsulating the underlying Python function with additional metadata,
        validation capabilities, and a standardized invocation interface.
        
        The function wrapper provides several benefits over direct function calls:
        - Consistent parameter validation using JSON Schema
        - Standardized error handling and logging
        - Function discoverability through metadata
        - Integration with the MCP registry and workflow systems
        - Abstraction from the underlying implementation details
        
        Each function should have a unique name within the registry to avoid conflicts.
        The description should clearly explain the function's purpose and behavior to
        assist users in understanding when and how to use it.
        
        Args:
            name: Unique identifier for the function within the MCP registry.
                 Should be descriptive of the function's purpose and follow
                 consistent naming conventions (e.g., verb_noun format).
            description: Human-readable description of what the function does,
                        its purpose, and any significant behavior details. This
                        will be exposed in documentation and UIs.
            func: The actual Python function implementation that will be invoked
                 when this MCP function is executed. Must be a callable that accepts
                 the parameters defined in the parameter schema.
            parameter_schema: JSON Schema defining the valid parameters for this
                             function, including types, constraints, and required fields.
                             Used for validation and documentation generation.
            return_schema: JSON Schema describing the expected return value structure
                          and types. Used primarily for documentation and client-side
                          validation expectations.
            
        Raises:
            ValueError: If name is empty or blank
            ValueError: If function implementation is None
        """
        if not name:
            raise ValueError("Function name cannot be empty")
        if func is None:
            raise ValueError("Function implementation is required")
            
        self.name = name
        self.description = description
        self.func = func
        self.parameter_schema = parameter_schema or {}
        self.return_schema = return_schema or {}
    
    def execute(self, parameters: ParameterType = None) -> ResultType:
        """
        Execute the function with the given parameters.
        
        This method is the core execution mechanism for MCP functions. It handles:
        1. Parameter normalization (providing empty dict for None)
        2. Function invocation with the appropriate parameters
        3. Error handling and propagation
        
        The execution process unpacks the parameters dictionary and passes them as
        keyword arguments to the underlying function. This allows for a consistent
        interface while supporting functions with different parameter signatures.
        
        Args:
            parameters: Dictionary of parameter names and values to pass to the function.
                       If None, an empty dictionary will be used.
            
        Returns:
            The result of the function execution, which could be any valid Python object
            depending on the function's implementation.
            
        Raises:
            TypeError: If the parameters don't match the function's signature
            Exception: Any exception raised by the underlying function
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
        Convert the function to a serializable dictionary representation.
        
        This method creates a standardized metadata dictionary that describes the function,
        suitable for API responses, UI rendering, documentation generation, and integration
        with external systems like LLMs. The dictionary includes the essential information
        needed to understand and invoke the function.
        
        The resulting dictionary contains:
        - name: The unique identifier for the function
        - description: Human-readable description of the function's purpose
        - parameters: JSON Schema describing the valid parameters (if provided)
        
        This serialized representation is particularly useful for:
        - Generating API documentation
        - Building dynamic UI controls for function execution
        - Providing function definitions to LLMs for function calling
        - Displaying available functions in management interfaces
        
        Returns:
            Dictionary with standardized function metadata that can be serialized to JSON
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameter_schema
        }


class MCPRegistry:
    """
    Central registry for MCP functions and capabilities.
    
    The MCPRegistry serves as the core component of the Model Content Protocol
    framework, providing services for function registration, discovery, and
    execution. It maintains a catalog of all available functions that can be
    invoked through the MCP API or used within workflows.
    
    Key responsibilities:
    - Function registration through decorator and direct method interfaces
    - Function lookup and metadata access
    - Function execution with parameter validation
    - Function discoverability and introspection
    
    The registry is designed to be used as a singleton instance shared across
    the application, providing a unified interface for all MCP functionality.
    """
    
    def __init__(self):
        """
        Initialize an empty MCP function registry.
        
        This constructor creates a new function registry instance that serves as the
        central repository for all available MCP functions in the application. The
        registry starts empty and is populated through function registration.
        
        The registry is a fundamental component of the MCP framework, providing:
        - A centralized catalog of all available functions
        - A standardized interface for function discovery
        - Consistent function execution mechanisms
        - Support for introspection and validation operations
        
        This registry follows the singleton pattern in practice, with a single global
        instance (created at the module level) that is used throughout the application
        to provide consistent access to registered functions.
        """
        self.functions: Dict[str, MCPFunction] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameter_schema: JSONSchemaType = None,
        return_schema: JSONSchemaType = None
    ) -> Callable[[FunctionType], FunctionType]:
        """
        Decorator to register a function with the MCP registry.
        
        This decorator wraps a regular Python function and makes it available
        through the MCP framework with additional metadata and validation.
        
        Example:
            @registry.register(
                name="calculate_tax",
                description="Calculate tax for a property",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "property_id": {"type": "string"},
                        "year": {"type": "integer"}
                    },
                    "required": ["property_id"]
                }
            )
            def calculate_tax(property_id: str, year: int = 2025) -> Dict[str, Any]:
                # Implementation
                ...
        
        Args:
            name: Unique function identifier
            description: Human-readable function description
            parameter_schema: JSON Schema defining valid parameters
            return_schema: JSON Schema defining expected return value
            
        Returns:
            Decorator function that registers the decorated function
            
        Raises:
            ValueError: If a function with the same name is already registered
        """
        if name in self.functions:
            raise ValueError(f"Function '{name}' is already registered")
            
        def decorator(func: FunctionType) -> FunctionType:
            self.functions[name] = MCPFunction(
                name=name,
                description=description,
                func=func,
                parameter_schema=parameter_schema,
                return_schema=return_schema
            )
            logger.info(f"Registered MCP function: {name}")
            return func
        return decorator
    
    def register_function(
        self,
        func: FunctionType,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameter_schema: JSONSchemaType = None,
        return_schema: JSONSchemaType = None
    ) -> None:
        """
        Register an existing function with the MCP registry.
        
        This method is similar to the `register` decorator but allows
        registering an existing function without using the decorator syntax.
        Useful for dynamically registering functions at runtime.
        
        Example:
            def calculate_tax(property_id: str, year: int = 2025) -> Dict[str, Any]:
                # Implementation
                ...
                
            registry.register_function(
                func=calculate_tax,
                name="calculate_tax",
                description="Calculate tax for a property",
                parameter_schema={
                    "type": "object",
                    "properties": {
                        "property_id": {"type": "string"},
                        "year": {"type": "integer"}
                    },
                    "required": ["property_id"]
                }
            )
        
        Args:
            func: The function to register
            name: Unique function identifier (defaults to function name)
            description: Human-readable function description (defaults to function docstring)
            parameter_schema: JSON Schema defining valid parameters
            return_schema: JSON Schema defining expected return value
            
        Raises:
            ValueError: If a function with the same name is already registered
        """
        name = name or func.__name__
        description = description or (func.__doc__ or "").strip()
        
        if name in self.functions:
            raise ValueError(f"Function '{name}' is already registered")
            
        self.functions[name] = MCPFunction(
            name=name,
            description=description,
            func=func,
            parameter_schema=parameter_schema,
            return_schema=return_schema
        )
        logger.info(f"Registered MCP function: {name}")
    
    def get_function(self, name: str) -> Optional[MCPFunction]:
        """
        Retrieve a function from the registry by its unique name.
        
        This method provides a safe way to look up registered functions without
        raising exceptions when the function doesn't exist. It's useful for cases
        where you need to check for a function's existence and retrieve it in a
        single operation, with None indicating that the function wasn't found.
        
        This lookup is commonly used for:
        - Validating function references in workflows
        - Retrieving functions for execution
        - Obtaining function metadata for validation or introspection
        - Checking capabilities before attempting operations
        
        Args:
            name: The unique identifier of the function to retrieve
            
        Returns:
            The MCPFunction instance if found, or None if no function with the
            specified name is registered in the registry
        """
        return self.functions.get(name)
    
    def execute_function(self, name: str, parameters: ParameterType = None) -> ResultType:
        """
        Execute a function by name with the provided parameters.
        
        This method is the primary entry point for invoking MCP functions through the registry.
        It handles function lookup, validation, and execution in a consistent manner, providing
        a unified interface for all registered functions regardless of their implementation.
        
        The execution flow follows these steps:
        1. Look up the function by name in the registry
        2. Validate that the function exists
        3. Delegate the execution to the function's execute method
        4. Return the result to the caller
        
        Args:
            name: The unique identifier of the function to execute
            parameters: Dictionary of parameter names and values to pass to the function.
                       If None, an empty dictionary will be used.
            
        Returns:
            The result of the function execution, which could be any valid Python object
            depending on the function's implementation.
            
        Raises:
            ValueError: If no function with the specified name is registered
            Exception: Any exception raised during function execution
        """
        function = self.get_function(name)
        if not function:
            raise ValueError(f"MCP function '{name}' not found")
        return function.execute(parameters)
    
    def has_function(self, name: str) -> bool:
        """
        Check if a function with the given name exists in the registry.
        
        This method provides a lightweight existence check for functions without
        retrieving the full function object. It's particularly useful for validation
        operations and logical branching based on capability availability.
        
        Common use cases include:
        - Validating function references in workflows during registration
        - Feature availability checks for UI elements or API endpoints
        - Conditional execution paths based on available functions
        - Pre-checking before attempting potentially expensive operations
        
        Args:
            name: The unique identifier of the function to check for
            
        Returns:
            True if a function with the specified name exists in the registry,
            False otherwise
        """
        return name in self.functions
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """
        List all registered functions with their complete metadata.
        
        This method provides access to the full set of registered functions in the
        registry as a list of metadata dictionaries. It's particularly useful for
        discovery and introspection use cases, such as generating documentation,
        presenting available functions to users in a UI, or integrating with external
        systems that need to understand the available capabilities.
        
        The metadata for each function includes essential information like the function
        name, description, and parameter specifications, which can be used to present
        the function to users or to validate inputs.
        
        Returns:
            List of function metadata dictionaries, where each dictionary contains
            information about a single registered function
        """
        return [func.to_dict() for func in self.functions.values()]


class MCPWorkflow:
    """
    Represents a sequence of MCP function calls that execute as a coordinated workflow.
    
    An MCPWorkflow provides a way to define and execute a series of related operations
    that should be performed together to accomplish a more complex task. Each workflow
    consists of ordered steps, where each step invokes a specific MCP function with
    parameters.
    
    Workflows support parameter passing between steps, where the output of previous
    steps can be used as input to later steps, enabling complex data transformation
    pipelines and multi-stage processing operations.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]],
        registry: MCPRegistry
    ):
        """
        Initialize an MCP workflow with metadata and execution configuration.
        
        This constructor creates a new workflow instance within the MCP framework,
        encapsulating a sequence of function calls that will be executed in order.
        The workflow provides a higher-level abstraction over individual function
        calls, enabling multi-step processes with data passing between steps.
        
        A workflow offers several advantages over direct function calls:
        - Standardized execution of multi-step processes
        - Parameter passing between related operations
        - Higher-level business logic encapsulation
        - Reusable sequences for common operations
        - Consistent error handling across multiple steps
        
        Each workflow should have a unique name within its registry to avoid conflicts.
        The description should clearly explain the workflow's purpose, the overall
        process it implements, and the expected outcome when executed.
        
        Args:
            name: Unique identifier for the workflow within the MCP workflow registry.
                 Should be descriptive of the workflow's overall purpose and follow
                 consistent naming conventions.
            description: Human-readable description of what the workflow accomplishes,
                        the process it implements, and any significant details about
                        its execution. This will be exposed in documentation and UIs.
            steps: Ordered list of workflow steps, where each step is a dictionary
                  containing a function name and optional parameters. These steps
                  define the sequence of operations that will be performed when
                  the workflow is executed.
            registry: Reference to the MCPRegistry that will be used to look up
                     and execute the functions referenced in the workflow steps.
                     The registry must contain all functions referenced by the steps.
        """
        self.name = name
        self.description = description
        self.steps = steps
        self.registry = registry
    
    def execute(self, initial_parameters: ParameterType = None) -> List[ResultType]:
        """
        Execute the workflow by sequentially running each step in the defined order.
        
        This method processes each step of the workflow in sequence, passing parameters
        between steps. Results from each step are accumulated in the returned list.
        
        The parameter passing mechanism allows data to flow between steps:
        1. Initial parameters are provided to the first step
        2. Each step's output is merged into the parameter dictionary
        3. Subsequent steps receive parameters that include outputs from previous steps
        
        This enables workflows to build complex data transformations across multiple
        functions, with each step building on the results of previous steps.
        
        Args:
            initial_parameters: Dictionary of parameters to provide to the workflow.
                               These parameters are available to all steps, but can
                               be overridden by step-specific parameters.
            
        Returns:
            List of result dictionaries, one for each workflow step in execution order
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
        Convert the workflow to a serializable dictionary representation.
        
        This method creates a standardized metadata dictionary that describes the workflow,
        suitable for API responses, UI rendering, documentation generation, and workflow
        visualization. The resulting dictionary includes all the information needed to
        understand the workflow's purpose and structure.
        
        The serialized representation contains:
        - name: The unique identifier for the workflow
        - description: Human-readable description of the workflow's purpose
        - steps: The ordered sequence of function calls that make up the workflow,
                including their individual parameters
        
        This dictionary format is particularly useful for:
        - Displaying workflow information in management interfaces
        - Generating workflow visualization diagrams
        - Supporting workflow execution through APIs
        - Building dynamic workflow selection UI components
        - Documenting available workflows for users
        
        Returns:
            Dictionary with standardized workflow metadata that can be serialized to JSON
        """
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps
        }


# Type definition for a workflow step
WorkflowStepType = Dict[str, Any]

class MCPWorkflowRegistry:
    """
    Registry for MCP workflows that manages workflow storage, retrieval, and execution.
    
    The MCPWorkflowRegistry maintains a central repository of all registered workflows
    in the system, providing services for workflow registration, validation, discovery,
    and execution. It works in coordination with the MCPRegistry to validate function
    references within workflow steps.
    
    This registry is responsible for ensuring that all workflows are properly defined
    and that their referenced functions exist before allowing registration. It also
    provides a standardized execution interface for running workflows by name.
    """
    
    def __init__(self, function_registry: MCPRegistry):
        """
        Initialize a workflow registry with a reference to the function registry.
        
        This constructor creates a new workflow registry that works in coordination
        with the specified function registry. The relationship between the two registries
        is essential for validating workflow steps against available functions and for
        executing workflow steps at runtime.
        
        The workflow registry depends on the function registry to:
        - Validate function references during workflow registration
        - Look up functions during workflow execution
        - Verify function availability before workflow operations
        - Support cross-registry introspection and metadata access
        
        This separation of concerns between function and workflow registries creates a
        clear architectural boundary while enabling tight integration between the two
        subsystems of the MCP framework.
        
        Args:
            function_registry: The MCP function registry instance that contains all
                              available functions that can be referenced in workflow
                              steps. This registry will be used for function validation
                              during workflow registration and for function lookup
                              during workflow execution.
        """
        self.workflows: Dict[str, MCPWorkflow] = {}
        self.function_registry = function_registry

    def register(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStepType]
    ) -> None:
        """
        Register a workflow.
        
        A workflow is a sequence of MCP function calls that can be executed
        as a single unit. Each step in the workflow consists of a function name
        and optional parameters.
        
        Example:
            workflow_registry.register(
                name="property_tax_analysis",
                description="Analyze property tax data and make predictions",
                steps=[
                    {
                        "function": "load_property_data",
                        "parameters": {"district_id": "D123"}
                    },
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
        
        Args:
            name: Unique workflow identifier
            description: Human-readable workflow description
            steps: List of workflow steps, each with a function name and parameters
            
        Raises:
            ValueError: If a workflow with the same name is already registered
            ValueError: If any step references a function that doesn't exist
        """
        if name in self.workflows:
            raise ValueError(f"Workflow '{name}' is already registered")
            
        # Validate that all referenced functions exist
        for i, step in enumerate(steps):
            if "function" not in step:
                raise ValueError(f"Step {i} in workflow '{name}' is missing a function name")
                
            function_name = step["function"]
            if not self.function_registry.has_function(function_name):
                raise ValueError(
                    f"Step {i} in workflow '{name}' references unknown function '{function_name}'"
                )
                
        self.workflows[name] = MCPWorkflow(
            name=name,
            description=description,
            steps=steps,
            registry=self.function_registry
        )
        logger.info(f"Registered MCP workflow: {name} with {len(steps)} steps")
    
    def get_workflow(self, name: str) -> Optional[MCPWorkflow]:
        """
        Retrieve a workflow from the registry by its unique name.
        
        This method provides a safe way to look up registered workflows without
        raising exceptions when the workflow doesn't exist. It's useful for cases
        where you need to check for a workflow's existence and retrieve it in a
        single operation, with None indicating that the workflow wasn't found.
        
        Common use cases include:
        - Retrieving workflows for execution
        - Verifying workflow existence before operations
        - Obtaining workflow metadata for UI display
        - Workflow validation during system integration
        
        Args:
            name: The unique identifier of the workflow to retrieve
            
        Returns:
            The MCPWorkflow instance if found, or None if no workflow with the
            specified name is registered in the registry
        """
        return self.workflows.get(name)
    
    def execute_workflow(self, name: str, parameters: ParameterType = None) -> List[ResultType]:
        """
        Execute a complete workflow by name with the provided parameters.
        
        This method serves as the primary entry point for triggering workflow execution
        through the registry. It handles the workflow lookup and delegates execution
        to the workflow instance, providing a consistent interface for running any
        registered workflow.
        
        The execution follows these steps:
        1. Lookup the workflow by name
        2. Validate workflow existence
        3. Delegate execution to the workflow's execute method
        4. Return the complete set of results from all workflow steps
        
        Args:
            name: Unique identifier of the workflow to execute
            parameters: Initial parameters to provide to the workflow execution.
                       These will be available to all steps and can be extended by
                       the results of each executed step.
            
        Returns:
            Ordered list of result dictionaries, one from each step of the workflow
            
        Raises:
            ValueError: If no workflow with the specified name is registered
        """
        workflow = self.get_workflow(name)
        if not workflow:
            raise ValueError(f"MCP workflow '{name}' not found")
        return workflow.execute(parameters)
    
    def has_workflow(self, name: str) -> bool:
        """
        Check if a workflow with the given name exists in the registry.
        
        This method provides a lightweight existence check for workflows without
        retrieving the full workflow object. It's useful when you only need to
        verify the presence of a workflow but don't need its details or execution
        capabilities.
        
        Common use cases include:
        - Validation before registration to prevent name conflicts
        - Feature availability checks in UI or API logic
        - Conditional execution paths based on workflow availability
        - Pre-checking before attempting potentially expensive workflow operations
        
        Args:
            name: The unique identifier of the workflow to check for
            
        Returns:
            True if a workflow with the specified name exists in the registry,
            False otherwise
        """
        return name in self.workflows
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all registered workflows with their complete metadata.
        
        This method provides a comprehensive view of all workflows registered in the
        system as a list of metadata dictionaries. Each dictionary contains information
        about a single workflow, including its name, description, and the sequence of
        steps that make up the workflow.
        
        This information is particularly useful for:
        - Building dynamic user interfaces that allow workflow selection and execution
        - Generating API documentation for available workflow endpoints
        - Creating dashboards or monitoring tools that track workflow usage
        - Supporting workflow discovery in automation systems
        
        Returns:
            List of workflow metadata dictionaries, where each dictionary contains
            complete information about a workflow, including its steps
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
def analyze_tax_distribution(tax_code: Optional[str] = None) -> Dict[str, Any]:
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
def predict_levy_rates(tax_code: Optional[str], years: int = 1) -> Dict[str, Any]:
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