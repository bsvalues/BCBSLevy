#!/usr/bin/env python3
"""
Demonstration script for the ML Levy Impact Agent.

This script demonstrates how to use the ML Levy Impact Agent by:
1. Loading sample data from the levy_impact_sample.json file
2. Running a prediction using the agent
3. Displaying the prediction results and explanations
"""

import sys
import os
import json
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import the utils package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ml_levy_impact_agent import MLLevyImpactAgent


def load_sample_data() -> Dict[str, Any]:
    """Load sample data from the JSON file."""
    try:
        with open('levy_impact_sample.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        sys.exit(1)


def format_prediction_output(prediction: Dict[str, Any]) -> None:
    """Format and print the prediction output."""
    print("\n" + "="*80)
    print("ML LEVY IMPACT PREDICTION RESULTS")
    print("="*80)
    
    if prediction.get("status") != "success":
        print(f"ERROR: {prediction.get('error', 'Unknown error occurred')}")
        return
    
    impact = prediction.get("estimated_impact", {})
    
    print(f"Tax Per Property: ${impact.get('tax_per_property', 0):,.2f}")
    print(f"Total Levy:       ${impact.get('total_levy', 0):,.2f}")
    print(f"Levy Rate Change: {impact.get('levy_rate_change', 0):.2f}%")
    print(f"Confidence:       {prediction.get('confidence', 0)*100:.1f}%")
    
    print("\nIMPACT FACTORS:")
    for factor in prediction.get("impact_factors", []):
        print(f" - {factor}")
    
    print("\nEXPLANATIONS:")
    for explanation in prediction.get("explanations", []):
        print(f" - {explanation}")
        
    print("="*80)


def main():
    """Main entry point for the demo script."""
    print("ML Levy Impact Agent Demonstration")
    print("----------------------------------")
    
    # Load sample data
    sample_data = load_sample_data()
    print(f"Loaded sample data for a {sample_data.get('district_type', 'unknown')} district")
    
    # Initialize the agent
    agent = MLLevyImpactAgent()
    print("ML Levy Impact Agent initialized")
    
    # Make prediction
    print("\nMaking levy impact prediction...")
    prediction = agent.predict_levy_impact(sample_data)
    
    # Display prediction results
    format_prediction_output(prediction)
    
    # Get detailed explanation if prediction was successful
    if prediction.get("status") == "success":
        print("\nGenerating detailed explanation...\n")
        explanation = agent.explain_prediction(prediction)
        if "detailed_explanation" in explanation:
            print(explanation["detailed_explanation"])
    
    print("\nDemonstration complete")


if __name__ == "__main__":
    main()