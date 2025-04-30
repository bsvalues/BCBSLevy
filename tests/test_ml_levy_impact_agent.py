"""
Tests for the ML Levy Impact Agent.

This module provides tests for verifying the functionality of the ML Levy Impact Agent,
which predicts levy impacts using a pre-trained model.
"""

import unittest
import json
from unittest.mock import patch, MagicMock

from utils.ml_levy_impact_agent import MLLevyImpactAgent


class TestMLLevyImpactAgent(unittest.TestCase):
    """Test cases for the ML Levy Impact Agent."""

    def setUp(self):
        """Set up test environment."""
        # Initialize agent with mocked Claude service
        with patch('utils.ml_levy_impact_agent.get_claude_service') as mock_get_claude:
            mock_claude = MagicMock()
            mock_get_claude.return_value = mock_claude
            self.agent = MLLevyImpactAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.name, "MLLevyImpactAgent")
        self.assertEqual(self.agent.description, "Predicts levy impacts using machine learning")
        self.assertTrue("predict_levy_impact" in self.agent.capabilities)
        self.assertTrue(self.agent.model_initialized)
    
    def test_predict_levy_impact_basic(self):
        """Test basic levy impact prediction."""
        params = {
            "mill_rate": 1.5,
            "property_value": 200000,
            "levy_limit": 5000000,
            "prior_year_levy": 4800000,
            "district_type": "school",
            "year": 2025
        }
        
        result = self.agent.predict_levy_impact(params)
        
        # Verify structure of the result
        self.assertEqual(result["status"], "success")
        self.assertIn("estimated_impact", result)
        self.assertIn("confidence", result)
        self.assertIn("impact_factors", result)
        self.assertIn("explanations", result)
        
        # Verify estimated impacts are calculated
        self.assertIn("tax_per_property", result["estimated_impact"])
        self.assertIn("total_levy", result["estimated_impact"])
        self.assertIn("levy_rate_change", result["estimated_impact"])
        
        # Verify tax calculation is correct
        self.assertEqual(result["estimated_impact"]["tax_per_property"], params["property_value"] / 1000 * params["mill_rate"])
    
    def test_predict_levy_impact_missing_parameters(self):
        """Test prediction with missing parameters."""
        # Missing property_value
        params = {
            "mill_rate": 1.5,
            "levy_limit": 5000000,
            "prior_year_levy": 4800000,
            "district_type": "school",
            "year": 2025
        }
        
        result = self.agent.predict_levy_impact(params)
        
        self.assertEqual(result["status"], "failed")
        self.assertIn("error", result)
        self.assertIn("Missing required parameter", result["error"])
    
    def test_predict_levy_impact_with_new_construction(self):
        """Test prediction including new construction value."""
        params = {
            "mill_rate": 1.5,
            "property_value": 200000,
            "levy_limit": 5000000,
            "prior_year_levy": 4800000,
            "district_type": "school",
            "year": 2025,
            "new_construction_value": 10000000
        }
        
        result = self.agent.predict_levy_impact(params)
        
        # Check that new construction is included in impact factors
        self.assertIn("New construction adds capacity", result["impact_factors"])
    
    @patch('utils.ml_levy_impact_agent.execute_anthropic_query')
    def test_explain_prediction(self, mock_execute_query):
        """Test prediction explanation generation."""
        # Mock the Claude response
        mock_execute_query.return_value = "This is a sample explanation of the prediction."
        
        # Create a prediction result
        prediction_result = {
            "estimated_impact": {
                "tax_per_property": 300.0,
                "total_levy": 4900000.0,
                "levy_rate_change": 2.08
            },
            "confidence": 0.85,
            "impact_factors": ["New construction adds capacity", "Near levy limit threshold"],
            "status": "success"
        }
        
        result = self.agent.explain_prediction(prediction_result)
        
        # Verify explanation is returned
        self.assertEqual(result["status"], "success")
        self.assertIn("detailed_explanation", result)
        self.assertEqual(result["detailed_explanation"], "This is a sample explanation of the prediction.")
        
        # Verify Claude was called with appropriate prompt
        mock_execute_query.assert_called_once()
        prompt = mock_execute_query.call_args[0][0]
        self.assertIn("levy impact prediction", prompt)
        self.assertIn("Tax Per Property: $300.00", prompt)
        self.assertIn("Confidence: 85.0%", prompt)


if __name__ == '__main__':
    unittest.main()