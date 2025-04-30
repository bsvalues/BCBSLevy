"""
Machine Learning Levy Impact Agent for impact prediction.

This module provides a specialized ML-based agent for predicting 
levy impacts using a pre-trained model. The agent loads the model
and provides prediction capabilities for the MCP framework.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional, Union

from utils.anthropic_utils import get_claude_service
from utils.mcp_core import registry
from utils.mcp_agents import MCPAgent

logger = logging.getLogger(__name__)


class MLLevyImpactAgent(MCPAgent):
    """
    Agent for predicting tax levy impacts using machine learning.
    
    This agent encapsulates a pre-trained machine learning model that can
    predict the impact of levy changes on taxpayers and jurisdictions.
    It accepts features related to property values, mill rates, and levy
    limits, then outputs impact estimations with confidence scores.
    """
    
    def __init__(self):
        """Initialize the ML Levy Impact Agent."""
        super().__init__(
            name="MLLevyImpactAgent",
            description="Predicts levy impacts using machine learning"
        )
        
        # Register capabilities
        self.register_capability("predict_levy_impact")
        
        # Claude service for AI capabilities and explanation
        self.claude = get_claude_service()
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """
        Load the pre-trained levy impact prediction model.
        
        In a production environment, this would load a trained model from disk
        or a model registry. For development purposes, we'll use a placeholder
        that simulates predictions.
        """
        logger.info("Initializing levy impact prediction model")
        # In a real implementation, load the model here
        # For example: self.model = tensorflow.keras.models.load_model("path/to/model")
        self.model_initialized = True
        logger.info("Levy impact prediction model initialized successfully")
    
    def predict_levy_impact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the impact of a levy change based on input features.
        
        Args:
            params: Dictionary containing the following prediction features:
                - mill_rate: Current mill rate (tax rate per $1,000 of assessed value)
                - property_value: Assessed property value
                - levy_limit: Maximum levy amount allowed by law
                - prior_year_levy: Previous year's levy amount
                - new_construction_value: Value of new construction in the district
                - district_type: Type of taxing district (e.g., "school", "fire", "city")
                - year: Target year for the prediction
                
        Returns:
            Dictionary containing:
                - estimated_impact: Predicted tax impact value
                - confidence: Confidence score (0-1) for the prediction
                - impact_factors: Key factors influencing the prediction
                - explanations: Human-readable explanations of the prediction
        """
        try:
            # Validate required parameters
            required_params = [
                "mill_rate", "property_value", "levy_limit", 
                "prior_year_levy", "district_type", "year"
            ]
            
            for param in required_params:
                if param not in params:
                    return {
                        "error": f"Missing required parameter: {param}",
                        "status": "failed"
                    }
            
            # Extract parameters
            mill_rate = float(params["mill_rate"])
            property_value = float(params["property_value"])
            levy_limit = float(params["levy_limit"])
            prior_year_levy = float(params["prior_year_levy"])
            district_type = params["district_type"]
            year = int(params["year"])
            
            # Optional parameters with defaults
            new_construction_value = float(params.get("new_construction_value", 0))
            
            # In a real implementation, we would:
            # 1. Preprocess the input features
            # 2. Pass them to the model for prediction
            # 3. Postprocess the model output
            
            # For demonstration, we'll use a dummy calculation
            # This would be replaced with actual model inference
            estimated_tax = (property_value / 1000) * mill_rate
            estimated_levy = min(prior_year_levy * 1.01 + (new_construction_value / 1000 * mill_rate), levy_limit)
            
            # Calculate levy rate change
            levy_rate_change = estimated_levy / prior_year_levy - 1 if prior_year_levy > 0 else 0
            
            # Generate confidence based on how close the estimated levy is to the levy limit
            confidence = 1.0 - (abs(estimated_levy - levy_limit) / levy_limit if levy_limit > 0 else 0)
            confidence = max(0.5, min(0.95, confidence))  # Limit confidence to 0.5-0.95 range
            
            # Generate impact factors
            impact_factors = []
            if new_construction_value > 0:
                impact_factors.append("New construction adds capacity")
            
            if estimated_levy > prior_year_levy * 1.03:
                impact_factors.append("Significant levy increase")
            
            if estimated_levy > prior_year_levy and estimated_levy >= levy_limit * 0.95:
                impact_factors.append("Near levy limit threshold")
            
            # Generate human-readable explanations
            explanations = [
                f"Estimated impact calculated based on property value of ${property_value:,.2f} at a mill rate of {mill_rate:.4f}.",
                f"Property would contribute approximately ${estimated_tax:,.2f} to the levy.",
                f"Total estimated levy of ${estimated_levy:,.2f} compared to prior year levy of ${prior_year_levy:,.2f}."
            ]
            
            if estimated_levy >= levy_limit:
                explanations.append(f"The district has reached its levy limit of ${levy_limit:,.2f}.")
            
            # Return prediction results
            return {
                "estimated_impact": {
                    "tax_per_property": estimated_tax,
                    "total_levy": estimated_levy,
                    "levy_rate_change": levy_rate_change * 100  # Convert to percentage
                },
                "confidence": confidence,
                "impact_factors": impact_factors,
                "explanations": explanations,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error predicting levy impact: {str(e)}")
            return {
                "error": f"Failed to predict levy impact: {str(e)}",
                "status": "failed"
            }
    
    def explain_prediction(self, prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed explanation of the impact prediction using Claude.
        
        Args:
            prediction_result: The result from predict_levy_impact
            
        Returns:
            Detailed explanation of the prediction
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "explanation": "Detailed explanation not available"
            }
        
        try:
            # Format the prediction data for Claude
            impact_data = {
                "prediction": prediction_result.get("estimated_impact", {}),
                "confidence": prediction_result.get("confidence", 0),
                "factors": prediction_result.get("impact_factors", [])
            }
            
            # Get explanation from Claude
            from utils.anthropic_utils import execute_anthropic_query
            
            prompt = f"""
            As a property tax expert, explain this levy impact prediction in detail:
            
            PREDICTION DATA:
            - Tax Per Property: ${impact_data['prediction'].get('tax_per_property', 0):,.2f}
            - Total Levy: ${impact_data['prediction'].get('total_levy', 0):,.2f}
            - Levy Rate Change: {impact_data['prediction'].get('levy_rate_change', 0):.2f}%
            - Confidence: {impact_data['confidence'] * 100:.1f}%
            
            KEY FACTORS:
            """
            
            # Add impact factors
            for factor in impact_data['factors']:
                prompt += f"- {factor}\n"
            
            prompt += """
            Provide a 2-3 paragraph explanation of this prediction that:
            1. Explains what these numbers mean for taxpayers
            2. Interprets the confidence level
            3. Clarifies how the factors influenced the prediction
            4. Suggests potential implications for the jurisdiction
            
            Make the explanation conversational and easy to understand for non-experts.
            """
            
            # Execute Claude query
            explanation = execute_anthropic_query(prompt)
            
            return {
                "detailed_explanation": explanation,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error explaining prediction: {str(e)}")
            return {
                "error": f"Failed to explain prediction: {str(e)}",
                "explanation": "Explanation unavailable due to an error",
                "status": "failed"
            }