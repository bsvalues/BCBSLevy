#!/usr/bin/env python3
"""
Command-line interface for the ML Levy Impact Agent.

This tool provides a command-line interface for making predictions
using the ML Levy Impact Agent without requiring the full Flask application.
"""

import argparse
import json
import sys
import logging
import os
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import the utils package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ml_levy_impact_agent import MLLevyImpactAgent


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='ML Levy Impact Prediction Tool')
    parser.add_argument('--input', '-i', type=str, help='JSON input file with prediction parameters')
    parser.add_argument('--output', '-o', type=str, help='Output file for prediction results (default: stdout)')
    parser.add_argument('--explain', '-e', action='store_true', help='Include detailed explanation in output')
    parser.add_argument('--mill-rate', type=float, help='Mill rate (tax per $1,000 of value)')
    parser.add_argument('--property-value', type=float, help='Property value')
    parser.add_argument('--levy-limit', type=float, help='Levy limit')
    parser.add_argument('--prior-year-levy', type=float, help='Prior year levy amount')
    parser.add_argument('--district-type', type=str, help='District type (e.g., school, fire, city)')
    parser.add_argument('--year', type=int, help='Target year for prediction')
    parser.add_argument('--new-construction-value', type=float, help='Value of new construction')
    
    return parser.parse_args()


def main():
    """Main entry point for the CLI tool."""
    args = parse_args()
    
    # Initialize the agent
    logger.info("Initializing ML Levy Impact Agent")
    agent = MLLevyImpactAgent()
    
    # Get prediction parameters from file or command-line args
    params = {}
    if args.input:
        try:
            with open(args.input, 'r') as f:
                params = json.load(f)
            logger.info(f"Loaded parameters from {args.input}")
        except Exception as e:
            logger.error(f"Error loading input file: {str(e)}")
            return 1
    else:
        # Collect parameters from command-line args
        if args.mill_rate is not None:
            params['mill_rate'] = args.mill_rate
        if args.property_value is not None:
            params['property_value'] = args.property_value
        if args.levy_limit is not None:
            params['levy_limit'] = args.levy_limit
        if args.prior_year_levy is not None:
            params['prior_year_levy'] = args.prior_year_levy
        if args.district_type is not None:
            params['district_type'] = args.district_type
        if args.year is not None:
            params['year'] = args.year
        if args.new_construction_value is not None:
            params['new_construction_value'] = args.new_construction_value
    
    # Validate parameters
    required_params = [
        "mill_rate", "property_value", "levy_limit", 
        "prior_year_levy", "district_type", "year"
    ]
    
    missing_params = [param for param in required_params if param not in params]
    if missing_params:
        logger.error(f"Missing required parameters: {', '.join(missing_params)}")
        logger.error("Please provide all required parameters either via input file or command-line arguments")
        return 1
    
    # Make prediction
    logger.info("Making levy impact prediction")
    prediction_result = agent.predict_levy_impact(params)
    
    # Generate explanation if requested
    if args.explain and prediction_result['status'] == 'success':
        logger.info("Generating detailed explanation")
        explanation = agent.explain_prediction(prediction_result)
        prediction_result['detailed_explanation'] = explanation.get('detailed_explanation')
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(prediction_result, f, indent=2)
        logger.info(f"Results written to {args.output}")
    else:
        print(json.dumps(prediction_result, indent=2))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())