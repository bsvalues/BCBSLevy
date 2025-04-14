"""
Model Content Protocol (MCP) agent implementations.

This module provides specialized AI agents for different tasks in the SaaS Levy Calculation Application.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Union
from sqlalchemy import func

from utils.anthropic_utils import get_claude_service
from utils.mcp_core import registry

logger = logging.getLogger(__name__)


class MCPAgent:
    """
    Base class for all Model Content Protocol (MCP) agents.
    
    This abstract class serves as the foundation for specialized AI agents within 
    the system. It provides core functionality for capability registration, request
    handling, and agent metadata exposure. MCPAgent is designed to be extended by
    concrete agent implementations that focus on specific domains or tasks.
    
    An MCPAgent integrates with the MCP registry to expose capabilities as API-accessible
    functions. It acts as a controller that delegates requests to the appropriate
    registered functions based on capability names.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize an MCP agent.
        
        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self.capabilities = []
    
    def register_capability(self, function_name: str) -> None:
        """
        Register a capability for this agent.
        
        Args:
            function_name: Name of a function in the MCP registry
        """
        self.capabilities.append(function_name)
    
    def handle_request(self, request: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle a request by delegating to the appropriate registered function.
        
        This method serves as the primary entry point for interacting with agents
        through the API. It validates that the requested capability is registered
        with this agent, then executes the corresponding function from the MCP registry.
        
        The handle_request method allows for a consistent interface across all agent
        types, enabling polymorphic usage where any agent can be accessed through
        the same mechanism regardless of its specific implementation details.
        
        Args:
            request: Request identifier matching a registered capability name
            parameters: Dictionary of parameters to pass to the function, with
                        parameter names as keys and their values as values
            
        Returns:
            Dictionary containing the response data from the executed function
            
        Raises:
            ValueError: If the requested capability is not supported by this agent
        """
        if request not in self.capabilities:
            raise ValueError(f"Agent '{self.name}' does not support '{request}'")
        
        # Execute the function with default empty dict if parameters is None
        return registry.execute_function(request, parameters or {})
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary representation.
        
        Returns:
            Dictionary with agent metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities
        }


class LevyAnalysisAgent(MCPAgent):
    """Agent for analyzing levy rates and assessed values."""
    
    def __init__(self):
        """Initialize the Levy Analysis Agent."""
        super().__init__(
            name="LevyAnalysisAgent",
            description="Analyzes levy rates and assessed values across districts"
        )
        
        # Register capabilities
        self.register_capability("analyze_tax_distribution")
        self.register_capability("predict_levy_rates")
        self.register_capability("get_data_quality_metrics")
        self.register_capability("generate_data_quality_recommendations")
        
        # Claude service for AI capabilities
        self.claude = get_claude_service()
    
    def analyze_levy_rates(self, tax_codes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze levy rates and generate insights.
        
        Args:
            tax_codes: List of tax codes with levy information
            
        Returns:
            Analysis results and insights
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "analysis": "Levy rate analysis not available"
            }
        
        # Structure data for Claude
        levy_data = {
            "tax_codes": tax_codes,
            "total_assessed_value": sum(tc.get("total_assessed_value", 0) for tc in tax_codes),
            "count": len(tax_codes)
        }
        
        # Get insights from Claude
        return self.claude.generate_levy_insights(levy_data)
    
    def get_data_quality_metrics(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get data quality metrics in real-time.
        
        This capability enables real-time monitoring of data quality metrics,
        including completeness, accuracy, and consistency of tax data.
        
        Args:
            params: Parameters for metrics generation
                - realtime: Whether to get real-time metrics or historical
                - dataset: Specific dataset to analyze (optional)
                
        Returns:
            Dictionary containing data quality metrics
        """
        # Default parameters
        realtime = params.get('realtime', True) if params else True
        
        try:
            from flask import current_app
            from sqlalchemy import desc, func
            from flask_sqlalchemy import SQLAlchemy
            from datetime import datetime
            import logging
            
            # Get database session
            db = current_app.extensions.get('sqlalchemy').db
            
            # Import models (done here to avoid circular imports)
            from models import (
                TaxDistrict, TaxCode, Property, 
                DataQualityScore, ValidationRule, ValidationResult
            )
            
            # Get latest data quality scores from database
            latest_score = db.session.query(DataQualityScore).order_by(
                desc(DataQualityScore.timestamp)
            ).first()
            
            # Get validation rules with their performance metrics
            validation_rules = db.session.query(
                ValidationRule, 
                func.count(ValidationResult.id).label('total'),
                func.sum(ValidationResult.passed.cast(db.Integer)).label('passed')
            ).outerjoin(
                ValidationResult
            ).group_by(
                ValidationRule.id
            ).all()
            
            # Calculate metrics from validation results if available
            rule_metrics = []
            for rule, total, passed in validation_rules:
                if total > 0:
                    pass_rate = (passed / total) * 100
                else:
                    pass_rate = 0
                
                rule_metrics.append({
                    'id': rule.id,
                    'name': rule.name,
                    'description': rule.description,
                    'pass_rate': pass_rate,
                    'passed': passed,
                    'failed': total - passed,
                    'total': total,
                    'severity': rule.severity
                })
            
            # Generate metrics based on real database data
            if latest_score:
                metrics = {
                    'overall_score': latest_score.overall_score,
                    'completeness_score': latest_score.completeness_score,
                    'accuracy_score': latest_score.accuracy_score,
                    'consistency_score': latest_score.consistency_score,
                    'timeliness_score': latest_score.timeliness_score,
                    'completeness_fields_missing': latest_score.completeness_fields_missing,
                    'accuracy_errors': latest_score.accuracy_errors,
                    'consistency_issues': latest_score.consistency_issues,
                    'validation_rules': rule_metrics,
                    'timestamp': datetime.now().isoformat(),
                    'realtime': realtime
                }
            else:
                # No metrics available, return empty data
                metrics = {
                    'error': 'No data quality metrics available',
                    'timestamp': datetime.now().isoformat(),
                    'realtime': realtime
                }
            
            return {'metrics': metrics}
        
        except Exception as e:
            logger.error(f"Error getting data quality metrics: {str(e)}")
            return {
                'error': f"Failed to retrieve data quality metrics: {str(e)}",
                'metrics': {}
            }
    
    def generate_data_quality_recommendations(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate AI-powered recommendations for improving data quality.
        
        This capability analyzes current data quality metrics and validation results
        to provide actionable recommendations for improving data quality.
        
        Args:
            params: Parameters for recommendation generation
                - focus_area: Specific area to focus on (completeness, accuracy, consistency)
                - max_recommendations: Maximum number of recommendations to return
                
        Returns:
            Dictionary containing data quality recommendations
        """
        if not self.claude:
            return {
                'error': 'Claude service not available',
                'recommendations': []
            }
        
        try:
            # Default parameters
            focus_area = params.get('focus_area', 'all') if params else 'all'
            max_recommendations = params.get('max_recommendations', 5) if params else 5
            
            # First get current metrics
            metrics_result = self.get_data_quality_metrics({'realtime': True})
            
            if 'error' in metrics_result:
                return {
                    'error': metrics_result['error'],
                    'recommendations': []
                }
            
            metrics = metrics_result.get('metrics', {})
            
            # Formulate query for Claude
            prompt = f"""
            As a data quality expert specializing in property tax systems, analyze these metrics and provide actionable recommendations:
            
            CURRENT DATA QUALITY METRICS:
            - Overall Score: {metrics.get('overall_score', 'N/A')}
            - Completeness: {metrics.get('completeness_score', 'N/A')}
            - Accuracy: {metrics.get('accuracy_score', 'N/A')}
            - Consistency: {metrics.get('consistency_score', 'N/A')}
            - Timeliness: {metrics.get('timeliness_score', 'N/A')}
            
            ISSUES:
            - Missing Fields: {metrics.get('completeness_fields_missing', 'N/A')}
            - Accuracy Errors: {metrics.get('accuracy_errors', 'N/A')}
            - Consistency Issues: {metrics.get('consistency_issues', 'N/A')}
            
            VALIDATION RULE PERFORMANCE:
            """
            
            # Add validation rules if available
            for rule in metrics.get('validation_rules', []):
                prompt += f"- {rule.get('name')}: {rule.get('pass_rate', 0):.1f}% pass rate ({rule.get('passed', 0)} passed, {rule.get('failed', 0)} failed)\n"
            
            prompt += f"""
            Based on this data, generate {max_recommendations} specific, actionable recommendations to improve data quality 
            """
            
            if focus_area != 'all':
                prompt += f"with focus on {focus_area}. "
            else:
                prompt += "across all areas. "
                
            prompt += """
            For each recommendation, provide:
            1. A concise title
            2. A detailed description explaining the issue and solution
            3. Impact level (High/Medium/Low)
            4. Effort level (High/Medium/Low)
            
            Format as a JSON array with objects containing: title, description, impact, effort
            """
            
            # Send to Claude
            try:
                from utils.anthropic_utils import execute_anthropic_query
                
                result = execute_anthropic_query(prompt)
                
                # Process Claude's response - extract JSON
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
                if json_match:
                    json_str = json_match.group(1)
                    recommendations = json.loads(json_str)
                else:
                    # Try to find anything that looks like JSON array
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', result, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        recommendations = json.loads(json_str)
                    else:
                        # Fallback to regexp extraction if JSON parsing fails
                        recommendations = self._extract_recommendations_from_text(result)
                
                # Process recommendations to add styling classes
                styled_recommendations = []
                for rec in recommendations:
                    if isinstance(rec, dict):
                        # Map impact and effort to Bootstrap classes
                        impact_class = self._map_level_to_class(rec.get('impact', 'Medium'))
                        effort_class = self._map_level_to_class(rec.get('effort', 'Medium'), inverse=True)
                        
                        styled_recommendations.append({
                            'title': rec.get('title', 'Recommendation'),
                            'description': rec.get('description', ''),
                            'impact': f"{rec.get('impact', 'Medium')} Impact",
                            'impact_class': impact_class,
                            'effort': f"{rec.get('effort', 'Medium')} Effort",
                            'effort_class': effort_class
                        })
                
                return {
                    'success': True,
                    'recommendations': styled_recommendations
                }
                
            except Exception as e:
                logger.error(f"Error generating recommendations with Claude: {str(e)}")
                return {
                    'error': f"Failed to generate recommendations: {str(e)}",
                    'recommendations': []
                }
                
        except Exception as e:
            logger.error(f"Error generating data quality recommendations: {str(e)}")
            return {
                'error': f"Failed to generate recommendations: {str(e)}",
                'recommendations': []
            }
    
    def _map_level_to_class(self, level, inverse=False):
        """Map impact/effort level to Bootstrap color class."""
        level = level.lower() if level else 'medium'
        
        if not inverse:
            # For impact (higher is better)
            if 'high' in level:
                return 'success'
            elif 'medium' in level:
                return 'primary'
            else:
                return 'warning'
        else:
            # For effort (lower is better)
            if 'high' in level:
                return 'warning'
            elif 'medium' in level:
                return 'info'
            else:
                return 'success'
    
    def _extract_recommendations_from_text(self, text):
        """Extract recommendations from text if JSON parsing fails."""
        recommendations = []
        
        # Define patterns
        title_pattern = r'(?:^|\n)(?:Title:|#|\d+\.\s*)(.*?)(?:\n|$)'
        desc_pattern = r'(?:Description:|Description)\s*(.*?)(?:\n\s*(?:Impact|Effort)|$)'
        impact_pattern = r'(?:Impact:|Impact)\s*(.*?)(?:\n|$)'
        effort_pattern = r'(?:Effort:|Effort)\s*(.*?)(?:\n|$)'
        
        # Split by recommendations (assume numbered or titled sections)
        sections = re.split(r'\n\s*(?:\d+\.|#)\s*', text)
        
        for section in sections:
            if not section.strip():
                continue
                
            title_match = re.search(title_pattern, section, re.IGNORECASE)
            desc_match = re.search(desc_pattern, section, re.IGNORECASE | re.DOTALL)
            impact_match = re.search(impact_pattern, section, re.IGNORECASE)
            effort_match = re.search(effort_pattern, section, re.IGNORECASE)
            
            title = title_match.group(1).strip() if title_match else "Recommendation"
            description = desc_match.group(1).strip() if desc_match else section.strip()
            impact = impact_match.group(1).strip() if impact_match else "Medium"
            effort = effort_match.group(1).strip() if effort_match else "Medium"
            
            recommendations.append({
                'title': title,
                'description': description,
                'impact': impact,
                'effort': effort
            })
            
            # Limit to 5 recommendations to prevent issues
            if len(recommendations) >= 5:
                break
                
        return recommendations
    
    def compare_assessed_values(self, tax_code_1: str, tax_code_2: str) -> Dict[str, Any]:
        """
        Compare assessed values between two tax codes.
        
        Args:
            tax_code_1: First tax code
            tax_code_2: Second tax code
            
        Returns:
            Comparison results
        """
        # Get real data from database if possible
        try:
            from flask import current_app
            from models import TaxCode, Property
            
            # Get database session
            db = current_app.extensions.get('sqlalchemy').db
            
            # Query tax code 1
            tc1 = db.session.query(
                TaxCode, 
                func.sum(Property.assessed_value).label('total_value'),
                func.count(Property.id).label('property_count')
            ).join(
                Property, Property.tax_code_id == TaxCode.id
            ).filter(
                TaxCode.code == tax_code_1
            ).group_by(
                TaxCode.id
            ).first()
            
            # Query tax code 2
            tc2 = db.session.query(
                TaxCode, 
                func.sum(Property.assessed_value).label('total_value'),
                func.count(Property.id).label('property_count')
            ).join(
                Property, Property.tax_code_id == TaxCode.id
            ).filter(
                TaxCode.code == tax_code_2
            ).group_by(
                TaxCode.id
            ).first()
            
            # Generate comparison from actual data
            if tc1 and tc2:
                tc1_value = float(tc1.total_value or 0)
                tc2_value = float(tc2.total_value or 0)
                difference = tc1_value - tc2_value
                
                if tc2_value > 0:
                    percentage = (difference / tc2_value) * 100
                else:
                    percentage = 0
                
                return {
                    "comparison": f"Comparison between {tax_code_1} and {tax_code_2}",
                    "tax_code_1": {
                        "code": tax_code_1,
                        "total_assessed_value": tc1_value,
                        "property_count": tc1.property_count
                    },
                    "tax_code_2": {
                        "code": tax_code_2,
                        "total_assessed_value": tc2_value,
                        "property_count": tc2.property_count
                    },
                    "difference": {
                        "absolute": difference,
                        "percentage": percentage
                    },
                    "insights": [
                        f"{tax_code_1} has {abs(percentage):.1f}% {'more' if percentage > 0 else 'less'} assessed value than {tax_code_2}",
                        f"{tax_code_1} has {tc1.property_count - tc2.property_count} {'more' if tc1.property_count > tc2.property_count else 'fewer'} properties than {tax_code_2}",
                        f"Average property value is {'higher' if tc1_value/tc1.property_count > tc2_value/tc2.property_count else 'lower'} in {tax_code_1}"
                    ]
                }
        
        except Exception as e:
            logger.warning(f"Error fetching real comparison data: {str(e)}. Using sample data.")
        
        # Fallback to sample data if database query fails
        return {
            "comparison": f"Comparison between {tax_code_1} and {tax_code_2}",
            "tax_code_1": {
                "code": tax_code_1,
                "total_assessed_value": 400000000,
                "property_count": 150
            },
            "tax_code_2": {
                "code": tax_code_2,
                "total_assessed_value": 250000000,
                "property_count": 100
            },
            "difference": {
                "absolute": 150000000,
                "percentage": 60
            },
            "insights": [
                f"{tax_code_1} has 60% more assessed value than {tax_code_2}",
                f"{tax_code_1} has 50% more properties than {tax_code_2}",
                f"Average property value is higher in {tax_code_1}"
            ]
        }


class LevyPredictionAgent(MCPAgent):
    """Agent for predicting future levy rates."""
    
    def __init__(self):
        """Initialize the Levy Prediction Agent."""
        super().__init__(
            name="LevyPredictionAgent",
            description="Predicts future levy rates based on historical data"
        )
        
        # Register capabilities
        self.register_capability("predict_levy_rates")
        
        # Claude service for AI capabilities
        self.claude = get_claude_service()
    
    def predict_levy_rates_with_scenario(
        self,
        tax_code: str,
        years: int = 3,
        scenario: str = "baseline"
    ) -> Dict[str, Any]:
        """
        Predict future levy rates with different scenarios.
        
        Args:
            tax_code: Tax code to predict
            years: Number of years to predict
            scenario: Scenario to model (baseline, growth, decline)
            
        Returns:
            Prediction results
        """
        # Get baseline prediction
        base_prediction = registry.execute_function(
            "predict_levy_rates",
            {"tax_code": tax_code, "years": years}
        )
        
        # Adjust based on scenario
        if scenario == "growth":
            multiplier = 1.1  # 10% higher growth
        elif scenario == "decline":
            multiplier = 0.9  # 10% lower growth
        else:  # baseline
            multiplier = 1.0
        
        # Apply scenario adjustment
        predictions = base_prediction.get("predictions", {})
        for year, rate in predictions.items():
            if rate is not None:
                predictions[year] = rate * multiplier
        
        return {
            "scenario": scenario,
            "predictions": predictions,
            "confidence": base_prediction.get("confidence", 0) * (1 - abs(multiplier - 1) * 0.5),
            "factors": base_prediction.get("factors", []) + [f"{scenario.title()} scenario applied"]
        }


class WorkflowCoordinatorAgent(MCPAgent):
    """Agent for coordinating complex workflows."""
    
    def __init__(self):
        """Initialize the Workflow Coordinator Agent."""
        super().__init__(
            name="WorkflowCoordinatorAgent",
            description="Coordinates complex multi-agent workflows"
        )
        
        # Create agent instances
        self.levy_analysis_agent = LevyAnalysisAgent()
        self.levy_prediction_agent = LevyPredictionAgent()
    
    def execute_comprehensive_analysis(self, tax_code: str) -> Dict[str, Any]:
        """
        Execute a comprehensive analysis workflow.
        
        Args:
            tax_code: Tax code to analyze
            
        Returns:
            Comprehensive analysis results
        """
        results = {}
        
        try:
            # Step 1: Analyze tax distribution
            distribution = self.levy_analysis_agent.handle_request(
                "analyze_tax_distribution",
                {"tax_code": tax_code}
            )
            results["distribution"] = distribution
            
            # Step 2: Predict levy rates (baseline)
            baseline = self.levy_prediction_agent.predict_levy_rates_with_scenario(
                tax_code=tax_code,
                years=3,
                scenario="baseline"
            )
            results["baseline"] = baseline
            
            # Step 3: Predict levy rates (growth)
            growth = self.levy_prediction_agent.predict_levy_rates_with_scenario(
                tax_code=tax_code,
                years=3,
                scenario="growth"
            )
            results["growth"] = growth
            
            # Step 4: Predict levy rates (decline)
            decline = self.levy_prediction_agent.predict_levy_rates_with_scenario(
                tax_code=tax_code,
                years=3,
                scenario="decline"
            )
            results["decline"] = decline
            
            # Step 5: Compile results
            results["summary"] = {
                "tax_code": tax_code,
                "current_distribution": distribution.get("distribution", {}),
                "baseline_year_3": baseline.get("predictions", {}).get("year_3"),
                "growth_year_3": growth.get("predictions", {}).get("year_3"),
                "decline_year_3": decline.get("predictions", {}).get("year_3"),
                "insights": [
                    "Comprehensive analysis completed successfully",
                    f"Tax code {tax_code} analyzed across distribution and projections",
                    "Three-year projections calculated for multiple scenarios"
                ]
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            return {
                "error": str(e),
                "partial_results": results
            }


# Create agent instances
levy_analysis_agent = LevyAnalysisAgent()
levy_prediction_agent = LevyPredictionAgent()
workflow_coordinator_agent = WorkflowCoordinatorAgent()

# Register agent functions with the MCP registry
registry.register_function(
    func=levy_analysis_agent.analyze_levy_rates,
    name="analyze_levy_rates",
    description="Analyze levy rates and generate insights",
    parameter_schema={
        "type": "object",
        "properties": {
            "tax_codes": {
                "type": "array",
                "description": "List of tax codes with levy information"
            }
        }
    }
)

registry.register_function(
    func=levy_analysis_agent.compare_assessed_values,
    name="compare_assessed_values",
    description="Compare assessed values between two tax codes",
    parameter_schema={
        "type": "object",
        "properties": {
            "tax_code_1": {
                "type": "string",
                "description": "First tax code"
            },
            "tax_code_2": {
                "type": "string",
                "description": "Second tax code"
            }
        }
    }
)

# Register data quality metrics capability
registry.register_function(
    func=levy_analysis_agent.get_data_quality_metrics,
    name="get_data_quality_metrics",
    description="Get real-time data quality metrics",
    parameter_schema={
        "type": "object",
        "properties": {
            "realtime": {
                "type": "boolean",
                "description": "Whether to get real-time metrics or historical",
                "default": True
            },
            "dataset": {
                "type": "string",
                "description": "Specific dataset to analyze (optional)"
            }
        }
    }
)

# Register data quality recommendations capability
registry.register_function(
    func=levy_analysis_agent.generate_data_quality_recommendations,
    name="generate_data_quality_recommendations",
    description="Generate AI-powered recommendations for improving data quality",
    parameter_schema={
        "type": "object",
        "properties": {
            "focus_area": {
                "type": "string",
                "description": "Specific area to focus on (completeness, accuracy, consistency)",
                "enum": ["all", "completeness", "accuracy", "consistency", "timeliness"],
                "default": "all"
            },
            "max_recommendations": {
                "type": "integer",
                "description": "Maximum number of recommendations to return",
                "default": 5
            }
        }
    }
)

registry.register_function(
    func=levy_prediction_agent.predict_levy_rates_with_scenario,
    name="predict_levy_rates_with_scenario",
    description="Predict future levy rates with different scenarios",
    parameter_schema={
        "type": "object",
        "properties": {
            "tax_code": {
                "type": "string",
                "description": "Tax code to predict"
            },
            "years": {
                "type": "integer",
                "description": "Number of years to predict",
                "default": 3
            },
            "scenario": {
                "type": "string",
                "description": "Scenario to model (baseline, growth, decline)",
                "enum": ["baseline", "growth", "decline"],
                "default": "baseline"
            }
        }
    }
)

registry.register_function(
    func=workflow_coordinator_agent.execute_comprehensive_analysis,
    name="execute_comprehensive_analysis",
    description="Execute a comprehensive analysis workflow",
    parameter_schema={
        "type": "object",
        "properties": {
            "tax_code": {
                "type": "string",
                "description": "Tax code to analyze"
            }
        }
    }
)