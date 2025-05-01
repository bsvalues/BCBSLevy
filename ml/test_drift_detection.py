"""
Test script for the TerraFusion drift detection and auto-retraining system.

This script tests the fixed boolean serialization in the drift detection system.
"""

import os
import sys
import json
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_drift_detection')

# Add parent directory to path to import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import our modules
from ml.hooks.drift_detector import DriftDetector, trigger_retraining
from ml.auto_retraining_scheduler import make_json_serializable

def test_drift_detection():
    """
    Test the drift detection functionality to ensure boolean values are properly serialized.
    """
    logger.info("Testing drift detection with boolean serialization fixes")
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    try:
        # Initialize drift detector
        detector = DriftDetector(
            model_path='ml/models/levy_impact_model.pkl',
            metrics_path='ml/models/model_metrics.json'
        )
        
        # Run drift detection
        logger.info("Running drift detection...")
        result = detector.monitor_and_alert(data_path='data/levy_training_data.csv')
        
        # Verify result structure
        logger.info("Drift detection complete, verifying results...")
        
        # Check that drift_detected is a string
        if 'drift_detected' not in result:
            logger.error("Missing 'drift_detected' key in results")
            return False
            
        if not isinstance(result['drift_detected'], str):
            logger.error(f"'drift_detected' is not a string, got: {type(result['drift_detected'])}")
            return False
            
        logger.info(f"Drift detected: {result['drift_detected']}")
        
        # Test JSON serialization - this should not raise an exception
        logger.info("Testing JSON serialization...")
        try:
            # Use the global serialization function
            serializable_result = make_json_serializable(result)
            json_str = json.dumps(serializable_result, indent=2)
            
            # Write to a test file
            with open('logs/drift_test_results.json', 'w') as f:
                f.write(json_str)
                
            logger.info("JSON serialization successful!")
            
            # Read back the file to verify
            with open('logs/drift_test_results.json', 'r') as f:
                test_read = json.load(f)
                logger.info("JSON deserialization successful!")
                
        except Exception as e:
            logger.error(f"Error in JSON serialization: {str(e)}")
            return False
            
        logger.info("All drift detection tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error in drift detection test: {str(e)}")
        return False

def test_retraining_trigger():
    """
    Test the retraining trigger functionality.
    """
    logger.info("Testing retraining trigger")
    
    try:
        # Create a sample drift result that would trigger retraining
        drift_result = {
            'drift_detected': 'True',
            'timestamp': datetime.now().isoformat()
        }
        
        # Test the trigger function
        logger.info("Testing retraining trigger with 'True' drift detected...")
        retrain_result = trigger_retraining(drift_result)
        
        if retrain_result != "True" and retrain_result != "False":
            logger.error(f"Retraining trigger returned unexpected value: {retrain_result}")
            return False
            
        logger.info(f"Retraining trigger returned: {retrain_result}")
        
        # Test with no drift
        drift_result = {
            'drift_detected': 'False',
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Testing retraining trigger with 'False' drift detected...")
        retrain_result = trigger_retraining(drift_result)
        
        if retrain_result != "False":
            logger.error(f"Retraining trigger should return 'False' but got: {retrain_result}")
            return False
            
        logger.info(f"Retraining trigger correctly returned: {retrain_result}")
        
        logger.info("All retraining trigger tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error in retraining trigger test: {str(e)}")
        return False

def main():
    """Main function for running the tests."""
    logger.info("Starting TerraFusion drift detection and retraining tests")
    
    test_results = {
        'drift_detection': test_drift_detection(),
        'retraining_trigger': test_retraining_trigger()
    }
    
    # Print overall results
    logger.info("Test Results:")
    for test_name, result in test_results.items():
        logger.info(f"  {test_name}: {'PASSED' if result else 'FAILED'}")
    
    # Determine overall success
    overall_success = all(test_results.values())
    
    if overall_success:
        logger.info("All tests PASSED!")
        return 0
    else:
        logger.error("Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())