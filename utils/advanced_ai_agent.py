"""
Advanced AI Agent Implementation for the Levy Calculation System.

This module provides advanced AI agent capabilities that extend the base MCP framework,
including:
- Multi-turn dialogue capabilities for complex analysis
- Cross-dataset insights to find connections between different data sources
- Contextual recommendations based on historical data patterns
- Natural language query interface for data exploration
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple, cast

from utils.anthropic_utils import get_claude_service, check_api_key_status
from utils.mcp_agents import MCPAgent
from utils.mcp_core import registry
from utils.html_sanitizer import sanitize_html, sanitize_mcp_insights
from utils.api_logging import APICallRecord, api_tracker

logger = logging.getLogger(__name__)

class AdvancedAnalysisAgent(MCPAgent):
    """
    Advanced AI agent with enhanced analysis capabilities.
    
    This agent extends the base MCPAgent with specialized capabilities for:
    - Advanced pattern recognition across datasets
    - Contextual recommendations based on historical trends
    - Natural language interaction for complex queries
    - Multi-step analysis workflows
    """
    
    def __init__(self):
        """
        Initialize the Advanced Analysis Agent with specialized capabilities.
        
        This constructor creates a new AdvancedAnalysisAgent instance with extended
        capabilities beyond the base MCPAgent. It sets up the agent's core components:
        
        1. Base agent configuration (name and description)
        2. Specialized analysis capabilities registration
        3. Claude service integration for AI-powered features
        4. Conversation history management for multi-turn dialogue
        
        The agent is designed as a singleton, with a single instance shared across
        the application through the get_advanced_analysis_agent() function. This
        ensures consistent state and conversation history management.
        
        Each capability registered by the agent corresponds to a method of the same
        name that implements the specific analytical function. These capabilities
        are integrated with the MCP registry to make them available through the API.
        
        Note:
            This initialization requires access to a valid Claude API key,
            which is handled by the get_claude_service() function. If the
            API key is missing or invalid, AI capabilities will be degraded
            but still accessible (with appropriate error handling).
        """
        super().__init__(
            name="AdvancedAnalysisAgent",
            description="Advanced AI agent with enhanced tax data analysis capabilities"
        )
        
        # Register specialized capabilities
        self.register_capability("analyze_cross_dataset_patterns")
        self.register_capability("generate_contextual_recommendations")
        self.register_capability("process_natural_language_query")
        self.register_capability("perform_multistep_analysis")
        
        # Claude service for AI capabilities
        self.claude = get_claude_service()
        
        # Conversation history for multi-turn dialogue
        self.conversation_history = []
        
    def analyze_cross_dataset_patterns(self, 
                                      tax_codes: List[Dict[str, Any]], 
                                      historical_rates: List[Dict[str, Any]], 
                                      property_records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze patterns across multiple datasets to find correlations and insights.
        
        This method uses the Claude AI to examine relationships between different
        tax-related datasets, identifying patterns, correlations, anomalies,
        and actionable insights that might not be apparent when analyzing each
        dataset in isolation.
        
        Args:
            tax_codes: Current tax code data containing information about tax districts,
                       rates, and associated metadata.
            historical_rates: Historical tax rate data showing how rates have changed
                              over time for different tax codes.
            property_records: Optional property assessment records with information
                              about individual properties, their assessed values,
                              and tax payments.
            
        Returns:
            Dict containing:
                - correlations: List of identified relationships between datasets
                - patterns: List of recurring patterns across the datasets
                - anomalies: List of unusual data points or outliers
                - insights: List of actionable insights derived from the analysis
                - error: Error message if analysis failed (only present on error)
        
        Raises:
            JSONDecodeError: If the AI response cannot be parsed as valid JSON
            Exception: For other errors during analysis
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "analysis": "Cross-dataset analysis not available"
            }
        
        # Structure data for Claude - limit to prevent token limits
        limited_tax_codes = tax_codes
        limited_historical_rates = historical_rates
        limited_property_records = property_records if property_records else []
        
        # Limit array data to prevent token limits
        if isinstance(tax_codes, list) and len(tax_codes) > 10:
            limited_tax_codes = []
            for i in range(10):  # Get first 10 items
                limited_tax_codes.append(tax_codes[i])
        if isinstance(historical_rates, list) and len(historical_rates) > 10:
            limited_historical_rates = []
            for i in range(10):  # Get first 10 items
                limited_historical_rates.append(historical_rates[i])
        if property_records and isinstance(property_records, list) and len(property_records) > 10:
            limited_property_records = []
            for i in range(10):  # Get first 10 items
                limited_property_records.append(property_records[i])
        
        analysis_data = {
            "tax_codes": limited_tax_codes,
            "historical_rates": limited_historical_rates,
            "property_records": limited_property_records
        }
        
        # Setup the prompt for cross-dataset analysis
        prompt = f"""
        Analyze the following tax datasets to identify cross-dataset patterns, correlations, and insights:
        
        Tax Code Data:
        {json.dumps(analysis_data['tax_codes'], indent=2)}
        
        Historical Rate Data:
        {json.dumps(analysis_data['historical_rates'], indent=2)}
        
        {"Property Record Data:" + json.dumps(analysis_data['property_records'], indent=2) if analysis_data['property_records'] else ""}
        
        Please provide:
        1. Key correlations between datasets
        2. Hidden patterns that emerge from cross-dataset analysis
        3. Anomalies that only appear when comparing multiple datasets
        4. Actionable insights based on these patterns
        
        Format your response as JSON with the following structure:
        {{
            "correlations": ["string", "string", ...],
            "patterns": ["string", "string", ...],
            "anomalies": ["string", "string", ...],
            "insights": ["string", "string", ...]
        }}
        """
        
        try:
            # Use Claude to generate cross-dataset analysis
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info("Successfully generated cross-dataset analysis")
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "correlations": [],
                "patterns": [],
                "anomalies": [],
                "insights": []
            }
        except Exception as e:
            logger.error(f"Error in cross-dataset analysis: {str(e)}")
            return {"error": sanitize_html(str(e))}
    
    def generate_contextual_recommendations(self, 
                                           tax_code_id: str,
                                           user_role: str = "administrator",
                                           focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate contextual recommendations based on a specific tax code and user role.
        
        This method analyzes tax code and historical data to generate tailored 
        recommendations for users based on their role and area of focus. It customizes
        the insights and actions based on whether the user is an administrator, analyst,
        or public user, emphasizing different aspects of the data accordingly.
        
        Args:
            tax_code_id: Identifier for the tax code
            user_role: Role of the user (administrator, analyst, public)
            focus_area: Specific area of focus for recommendations (optional)
            
        Returns:
            Dict containing:
                - user_role: The role of the user
                - focus_areas: List of focus areas for the recommendations
                - recommendations: List of recommendation objects, each containing:
                    - title: Brief title of the recommendation
                    - description: Detailed description of the recommendation
                    - justification: Data-driven justification for the recommendation
                    - priority: Priority level (high, medium, low)
                - error: Error message if recommendations generation failed (only present on error)
                
        Raises:
            JSONDecodeError: If the AI response cannot be parsed as valid JSON
            Exception: For other errors during recommendation generation
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "recommendations": []
            }
        
        # Get tax code data from the function registry
        tax_code_data = registry.execute_function(
            "get_tax_code_details",
            {"tax_code_id": tax_code_id}
        )
        
        # Get historical data from the function registry
        historical_data = registry.execute_function(
            "get_historical_rates",
            {"tax_code_id": tax_code_id}
        )
        
        # Determine focus areas based on user role if not specified
        if not focus_area:
            if user_role == "administrator":
                focus_areas = ["compliance", "policy", "efficiency"]
            elif user_role == "analyst":
                focus_areas = ["trends", "forecasting", "anomalies"]
            else:  # public
                focus_areas = ["transparency", "understanding", "planning"]
        else:
            focus_areas = [focus_area]
        
        # Setup the prompt for contextual recommendations
        prompt = f"""
        Generate contextual recommendations for tax code {tax_code_id} tailored for a {user_role}
        with focus on {', '.join(focus_areas)}.
        
        Tax Code Data:
        {json.dumps(tax_code_data, indent=2)}
        
        Historical Data:
        {json.dumps(historical_data, indent=2)}
        
        Please provide:
        1. Specific recommendations relevant to the user's role
        2. Actionable insights focused on {', '.join(focus_areas)}
        3. Data-driven justifications for each recommendation
        4. Priority level for each recommendation
        
        Format your response as JSON with the following structure:
        {{
            "user_role": "{user_role}",
            "focus_areas": {json.dumps(focus_areas)},
            "recommendations": [
                {{
                    "title": "string",
                    "description": "string",
                    "justification": "string",
                    "priority": "high|medium|low"
                }},
                // More recommendations...
            ]
        }}
        """
        
        try:
            # Use Claude to generate recommendations
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully generated recommendations for {user_role}")
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "user_role": user_role,
                "focus_areas": focus_areas,
                "recommendations": []
            }
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {"error": sanitize_html(str(e))}
    
    def process_natural_language_query(self, 
                                      query: str,
                                      context: Optional[Dict[str, Any]] = None,
                                      add_to_history: bool = True) -> Dict[str, Any]:
        """
        Process a natural language query about tax data.
        
        This method provides a conversational interface for users to ask questions
        about tax data in plain language. It maintains a conversation history
        to provide context-aware responses across multiple interactions and can
        incorporate additional contextual information provided with the query.
        
        Args:
            query: Natural language query from the user
            context: Additional context for the query such as selected tax codes,
                     districts, or specific data points (optional)
            add_to_history: Whether to add this interaction to the conversation
                           history for context in future queries
            
        Returns:
            Dict containing:
                - answer: The direct response to the user's query
                - relevant_data: Key data points relevant to the query
                - visualization_suggestions: List of suggested visualizations to present the data
                - follow_up_questions: List of potential follow-up questions the user might ask
                - error: Error message if query processing failed (only present on error)
                
        Raises:
            JSONDecodeError: If the AI response cannot be parsed as valid JSON
            Exception: For other errors during natural language processing
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "response": "Natural language processing not available"
            }
        
        # Add query to conversation history if enabled
        if add_to_history:
            self.conversation_history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
        
        # Prepare context for the query
        context_data = ""
        if context:
            context_data = f"Context Information:\n{json.dumps(context, indent=2)}\n\n"
        
        # Include relevant conversation history for continuity
        history_text = ""
        if self.conversation_history and len(self.conversation_history) > 1:
            history_text = "Previous conversation:\n"
            for i, entry in enumerate(self.conversation_history[:-1]):
                history_text += f"{entry['role'].title()}: {entry['content']}\n"
            history_text += "\n"
        
        # Setup the prompt for natural language processing
        prompt = f"""
        {history_text}
        {context_data}
        User Query: {query}
        
        Provide a comprehensive answer to the user's query about tax data, including:
        1. Direct answer to the query
        2. Relevant data and analysis
        3. Visualizations or data presentation suggestions if applicable
        4. Follow-up questions the user might be interested in
        
        Format your response as JSON with the following structure:
        {{
            "answer": "string",
            "relevant_data": {{
                // Key data points relevant to the query
            }},
            "visualization_suggestions": ["string", "string", ...],
            "follow_up_questions": ["string", "string", ...]
        }}
        """
        
        try:
            # Use Claude to process the query
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully processed natural language query: {query[:50]}...")
            
            # Add response to conversation history if enabled
            if add_to_history:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "answer": "I'm sorry, but I couldn't process your query properly. Please try asking in a different way.",
                "relevant_data": {},
                "visualization_suggestions": [],
                "follow_up_questions": [
                    "Can you rephrase your question?",
                    "Are you looking for specific tax information?",
                    "Would you like to see statistical data about tax rates?"
                ]
            }
        except Exception as e:
            logger.error(f"Error processing natural language query: {str(e)}")
            return {"error": sanitize_html(str(e))}
    
    def perform_multistep_analysis(self, 
                                  tax_district_id: str,
                                  analysis_type: str = "comprehensive",
                                  years: int = 3) -> Dict[str, Any]:
        """
        Perform a multi-step analysis workflow for a tax district.
        
        This method orchestrates a complex analytical workflow that combines data
        retrieval, statistical calculations, and AI-powered insights generation.
        It executes multiple steps in sequence, passing data between steps and
        ultimately generating a comprehensive analysis report that combines
        statistical metrics with interpretive insights.
        
        Args:
            tax_district_id: Identifier for the tax district to analyze
            analysis_type: Type of analysis to perform, one of:
                          - "comprehensive": Full analysis including all metrics
                          - "trend": Focus on trends and changes over time
                          - "compliance": Focus on regulatory compliance issues
            years: Number of historical years to include in the analysis
            
        Returns:
            Dict containing:
                - district_info: Basic information about the analyzed district
                - analysis_type: The type of analysis performed
                - years_analyzed: Number of years included in the analysis
                - tax_code_count: Number of tax codes in the district
                - insights: AI-generated insights based on the analysis, including:
                    - key_insights: List of main findings
                    - trends: List of identified trends
                    - anomalies: List of detected anomalies
                    - recommendations: List of strategic recommendations
                    - visualization_suggestions: List of visualization ideas
                - statistical_data: Raw statistical metrics calculated for the district
                - error: Error message if analysis failed (only present on error)
                
        Raises:
            Exception: For errors during any step of the analysis process
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "analysis": "Multi-step analysis not available"
            }
        
        try:
            # Step 1: Get district information
            district_info = registry.execute_function(
                "get_district_details",
                {"district_id": tax_district_id}
            )
            
            # Step 2: Get tax codes for the district
            tax_codes = registry.execute_function(
                "get_district_tax_codes",
                {"district_id": tax_district_id}
            )
            
            # Step 3: Get historical rates for the district
            historical_rates = registry.execute_function(
                "get_district_historical_rates",
                {"district_id": tax_district_id, "years": years}
            )
            
            # Step 4: Calculate statistical metrics based on analysis type
            if analysis_type == "comprehensive":
                statistical_analysis = registry.execute_function(
                    "calculate_comprehensive_statistics",
                    {"tax_codes": tax_codes, "historical_rates": historical_rates}
                )
            elif analysis_type == "trend":
                statistical_analysis = registry.execute_function(
                    "calculate_trend_statistics",
                    {"tax_codes": tax_codes, "historical_rates": historical_rates}
                )
            elif analysis_type == "compliance":
                statistical_analysis = registry.execute_function(
                    "calculate_compliance_statistics",
                    {"tax_codes": tax_codes, "historical_rates": historical_rates}
                )
            else:
                statistical_analysis = {}
            
            # Step 5: Use Claude to generate insights from all collected data
            # Create limited data to prevent token limits
            limited_tax_codes = tax_codes
            limited_historical_rates = historical_rates
            
            # Limit array data to prevent token limits
            if isinstance(tax_codes, list) and len(tax_codes) > 10:
                limited_tax_codes = []
                # Safely limit to first 10 items
                count = 0
                for item in tax_codes:
                    if count >= 10:
                        break
                    if isinstance(item, dict):
                        limited_tax_codes.append(dict(item))
                    else:
                        limited_tax_codes.append(item)
                    count += 1
            
            if isinstance(historical_rates, list) and len(historical_rates) > 10:
                limited_historical_rates = []
                # Safely limit to first 10 items
                count = 0
                for item in historical_rates:
                    if count >= 10:
                        break
                    if isinstance(item, dict):
                        limited_historical_rates.append(dict(item))
                    else:
                        limited_historical_rates.append(item)
                    count += 1
            
            combined_data = {
                "district_info": district_info,
                "tax_codes": limited_tax_codes,
                "historical_rates": limited_historical_rates,
                "statistical_analysis": statistical_analysis
            }
            
            # Setup the prompt for AI-powered insights
            prompt = f"""
            Generate insights for {analysis_type} analysis of tax district {tax_district_id}
            based on the following data:
            
            District Information:
            {json.dumps(combined_data['district_info'], indent=2)}
            
            Tax Code Data:
            {json.dumps(combined_data['tax_codes'], indent=2)}
            
            Historical Rate Data:
            {json.dumps(combined_data['historical_rates'], indent=2)}
            
            Statistical Analysis:
            {json.dumps(combined_data['statistical_analysis'], indent=2)}
            
            Please provide:
            1. Key insights from the {analysis_type} analysis
            2. Long-term trends and patterns
            3. Anomalies and areas of concern
            4. Strategic recommendations based on the analysis
            5. Visualizations that would best present this data
            
            Format your response as JSON with the following structure:
            {{
                "analysis_type": "{analysis_type}",
                "district_name": "{district_info.get('name', tax_district_id)}",
                "key_insights": ["string", "string", ...],
                "trends": ["string", "string", ...],
                "anomalies": ["string", "string", ...],
                "recommendations": ["string", "string", ...],
                "visualization_suggestions": ["string", "string", ...]
            }}
            """
            
            # Use Claude to generate insights
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully completed multi-step {analysis_type} analysis")
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            
            # Step 6: Combine all results into a comprehensive report
            final_result = {
                "district_info": district_info,
                "analysis_type": analysis_type,
                "years_analyzed": years,
                "tax_code_count": len(tax_codes),
                "insights": sanitized_result,
                "statistical_data": statistical_analysis
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in multi-step analysis: {str(e)}")
            return {
                "error": sanitize_html(str(e)),
                "analysis_type": analysis_type,
                "district_id": tax_district_id
            }
    
    def clear_conversation_history(self) -> None:
        """
        Clear the conversation history.
        
        This method resets the conversation history to an empty list,
        effectively starting a new conversation thread. This is useful when
        switching contexts or users, or when a conversation has reached its
        natural conclusion and a new topic is being discussed.
        
        Returns:
            None
        """
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history.
        
        This method retrieves the current conversation history, which contains
        all previous interactions between the user and the AI agent. Each entry
        in the history includes the role (user or assistant), the content of the
        message, and a timestamp.
        
        Returns:
            List of conversation entries, each containing:
                - role: The speaker role ("user" or "assistant")
                - content: The message content
                - timestamp: ISO 8601 formatted timestamp of when the message was added
        """
        return self.conversation_history


# Singleton instance to be created when needed
advanced_analysis_agent = None

def init_advanced_agent():
    """
    Initialize the advanced analysis agent and register its functions with MCP.
    
    This factory function creates and configures the singleton instance of 
    the AdvancedAnalysisAgent class, then registers all of its specialized
    analytical capabilities with the MCP registry. The registration process
    makes these capabilities available through the API and web interface.
    
    The initialization process includes:
    1. Creating the agent instance if it doesn't already exist
    2. Registering each agent capability with the MCP registry
    3. Setting up parameter schemas for each capability
    4. Configuring proper error handling for AI-dependent functions
    
    Each function is registered with a detailed JSON schema that defines
    the expected input parameters, their types, and validation rules.
    This enables automatic parameter validation and documentation
    generation throughout the application.
    
    The agent functions serve as an abstraction layer between the web
    application and the underlying AI services, providing:
    - Consistent error handling for AI service disruptions
    - Input validation and sanitization
    - Result formatting and structure normalization
    - Conversation state management across multiple requests
    
    Note:
        This function should be called within a Flask application context
        to ensure proper access to configuration and services. It is typically
        called during application startup from app.py after other core
        services have been initialized.
    
    Returns:
        AdvancedAnalysisAgent: The initialized agent instance, ready for use
                              throughout the application.
    
    Raises:
        RuntimeError: If called outside of a Flask application context
        ImportError: If required dependencies for AI services aren't available
        Exception: For other initialization errors (agent will still be created)
    """
    global advanced_analysis_agent
    
    if advanced_analysis_agent is None:
        # Create the singleton instance
        advanced_analysis_agent = AdvancedAnalysisAgent()
        
        # Register agent functions with the MCP registry
        registry.register_function(
            func=advanced_analysis_agent.analyze_cross_dataset_patterns,
            name="analyze_cross_dataset_patterns",
            description="Analyze patterns across multiple datasets to find correlations and insights",
            parameter_schema={
                "type": "object",
                "properties": {
                    "tax_codes": {
                        "type": "array",
                        "description": "Current tax code data"
                    },
                    "historical_rates": {
                        "type": "array",
                        "description": "Historical tax rate data"
                    },
                    "property_records": {
                        "type": "array",
                        "description": "Property assessment records (optional)"
                    }
                }
            }
        )
        
        registry.register_function(
            func=advanced_analysis_agent.generate_contextual_recommendations,
            name="generate_contextual_recommendations",
            description="Generate contextual recommendations based on a specific tax code and user role",
            parameter_schema={
                "type": "object",
                "properties": {
                    "tax_code_id": {
                        "type": "string",
                        "description": "Identifier for the tax code"
                    },
                    "user_role": {
                        "type": "string",
                        "description": "Role of the user (administrator, analyst, public)",
                        "default": "administrator"
                    },
                    "focus_area": {
                        "type": "string",
                        "description": "Specific area of focus for recommendations (optional)"
                    }
                }
            }
        )
        
        registry.register_function(
            func=advanced_analysis_agent.process_natural_language_query,
            name="process_natural_language_query",
            description="Process a natural language query about tax data",
            parameter_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for the query (optional)"
                    },
                    "add_to_history": {
                        "type": "boolean",
                        "description": "Whether to add this interaction to conversation history",
                        "default": True
                    }
                }
            }
        )
        
        registry.register_function(
            func=advanced_analysis_agent.perform_multistep_analysis,
            name="perform_multistep_analysis",
            description="Perform a multi-step analysis workflow for a tax district",
            parameter_schema={
                "type": "object",
                "properties": {
                    "tax_district_id": {
                        "type": "string",
                        "description": "Identifier for the tax district"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis to perform (comprehensive, trend, compliance)",
                        "default": "comprehensive"
                    },
                    "years": {
                        "type": "integer",
                        "description": "Number of years to include in the analysis",
                        "default": 3
                    }
                }
            }
        )
        
        registry.register_function(
            func=advanced_analysis_agent.clear_conversation_history,
            name="clear_conversation_history",
            description="Clear the conversation history",
            parameter_schema={
                "type": "object",
                "properties": {}
            }
        )
        
        registry.register_function(
            func=advanced_analysis_agent.get_conversation_history,
            name="get_conversation_history",
            description="Get the conversation history",
            parameter_schema={
                "type": "object",
                "properties": {}
            }
        )
        
        logger.info("Advanced Analysis Agent initialized and registered")
    
    return advanced_analysis_agent

def get_advanced_analysis_agent():
    """
    Get the advanced analysis agent instance, initializing it if necessary.
    
    This function serves as the primary access point for obtaining the singleton
    AdvancedAnalysisAgent instance throughout the application. It provides a
    fault-tolerant mechanism for accessing the agent by:
    
    1. Checking if the agent has already been initialized
    2. Initializing it through init_advanced_agent() if needed
    3. Providing comprehensive error handling for initialization failures
    4. Ensuring a valid agent instance is always returned, even after errors
    5. Centralizing access to prevent multiple initialization attempts
    
    The function implements a defensive approach to agent initialization, catching
    and logging all possible exceptions during the initialization process, but
    still ensuring that a usable agent instance is returned. This ensures that
    AI-dependent features degrade gracefully rather than completely failing if 
    there are issues with the underlying AI services or initialization process.
    
    This is the preferred way to access the agent throughout the application, as it:
    - Guarantees a valid instance will always be returned
    - Handles initialization transparently without client code needing to check
    - Centralizes error handling for initialization issues
    - Maintains the singleton pattern to ensure consistent conversation state
    - Provides detailed logging for troubleshooting initialization issues
    
    Example:
        agent = get_advanced_analysis_agent()
        results = agent.process_natural_language_query("Analyze tax rates for 2024")
    
    Returns:
        AdvancedAnalysisAgent: The singleton agent instance, ready for use.
                              If initialization fails, a basic instance without
                              registered functions will be returned that handles
                              errors gracefully in its method implementations.
    """
    global advanced_analysis_agent
    if advanced_analysis_agent is None:
        try:
            advanced_analysis_agent = init_advanced_agent()
            if advanced_analysis_agent is None:
                logging.error("Failed to initialize advanced analysis agent")
                # Create a new instance if initialization failed
                advanced_analysis_agent = AdvancedAnalysisAgent()
        except Exception as e:
            logging.error(f"Error initializing advanced analysis agent: {str(e)}")
            # Create a new instance if initialization failed with an exception
            advanced_analysis_agent = AdvancedAnalysisAgent()
    return advanced_analysis_agent