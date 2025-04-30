"""
Demonstration script for the auto-retraining pipeline and drift detection.

This script demonstrates the key components of the TerraFusion 
auto-retraining pipeline, including:
1. Initial model training
2. Drift detection
3. Automatic retraining when drift is detected
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('retraining_demo')

def run_initial_training():
    """Run the initial model training"""
    from training.retrain_pipeline import RetrainPipeline
    
    logger.info("=== Running Initial Model Training ===")
    
    # Create and run the pipeline
    pipeline = RetrainPipeline()
    metrics = pipeline.run()
    
    logger.info(f"Initial training complete: MSE={metrics['mse']:.4f}, R²={metrics['r2']:.4f}")
    return metrics

def simulate_data_drift():
    """Simulate data drift by creating modified data"""
    logger.info("=== Simulating Data Drift ===")
    
    # Load the original data
    data = pd.read_csv('data/levy_training_data.csv')
    
    # Make a copy for drift simulation
    drift_data = data.copy()
    
    # Add a fixed offset to create drift
    drift_offset = 8.5
    drift_data['forecast'] = drift_data['forecast'] + drift_offset
    
    # Save to a new file
    drift_data_path = 'data/levy_drift_data.csv'
    drift_data.to_csv(drift_data_path, index=False)
    
    logger.info(f"Drift data created with offset of {drift_offset}")
    return drift_data_path

def check_for_drift(data_path):
    """Check for drift using the drift detector"""
    from hooks.drift_detector import DriftDetector
    
    logger.info("=== Checking for Drift ===")
    
    # Create drift detector
    detector = DriftDetector()
    
    # Import here to avoid circular imports
    import joblib
    model_path = 'ml/models/levy_impact_model.pkl'
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        return None
        
    model = joblib.load(model_path)
    
    # Load data
    data = pd.read_csv(data_path)
    
    # Check for drift
    distribution_drift = detector.check_distribution_drift(data)
    prediction_drift = detector.check_prediction_drift(model, data)
    
    # Combine results
    drift_detected = distribution_drift['drift_detected'] or prediction_drift['drift_detected']
    
    result = {
        'status': 'alert' if drift_detected else 'ok',
        'drift_detected': drift_detected,
        'distribution_drift': distribution_drift,
        'prediction_drift': prediction_drift,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Drift detection result: {result['status']}")
    logger.info(f"Drift detected: {result['drift_detected']}")
    
    return result

def run_retraining(data_path):
    """Run model retraining with the new data"""
    from training.retrain_pipeline import RetrainPipeline
    
    logger.info("=== Running Model Retraining ===")
    
    # Create and run the pipeline with drift data
    pipeline = RetrainPipeline()
    metrics = pipeline.run(csv_path=data_path)
    
    logger.info(f"Retraining complete: MSE={metrics['mse']:.4f}, R²={metrics['r2']:.4f}")
    return metrics

def evaluate_improvement():
    """Evaluate the improvement from retraining"""
    logger.info("=== Evaluating Retraining Improvement ===")
    
    # Load training history if available
    history_path = 'ml/models/training_history.csv'
    if not os.path.exists(history_path):
        logger.warning(f"Training history file not found: {history_path}")
        return
        
    history = pd.read_csv(history_path)
    
    if len(history) < 2:
        logger.warning("Not enough training runs to evaluate improvement")
        return
        
    # Compare metrics from first and last training
    first_run = history.iloc[0]
    last_run = history.iloc[-1]
    
    mse_change = (last_run['mse'] - first_run['mse']) / first_run['mse']
    r2_change = (last_run['r2'] - first_run['r2']) / (1 - first_run['r2'] if first_run['r2'] != 1 else 0.001)
    
    logger.info(f"MSE change after retraining: {mse_change:.2%}")
    logger.info(f"R² change after retraining: {r2_change:.2%}")
    
    return {
        'mse_change': mse_change,
        'r2_change': r2_change,
        'first_run': first_run.to_dict(),
        'last_run': last_run.to_dict()
    }

def main():
    """Main function to run the demo"""
    logger.info("Starting TerraFusion Auto-Retraining Pipeline Demo")
    
    try:
        # Make sure the models directory exists
        os.makedirs('ml/models', exist_ok=True)
        
        # Step 1: Initial training
        initial_metrics = run_initial_training()
        
        # Step 2: Simulate data drift
        drift_data_path = simulate_data_drift()
        
        # Step 3: Check for drift
        drift_result = check_for_drift(drift_data_path)
        
        # Step 4: Run retraining if drift detected
        if drift_result['drift_detected']:
            retrain_metrics = run_retraining(drift_data_path)
            
            # Step 5: Evaluate improvement
            improvement = evaluate_improvement()
            
            logger.info("Auto-retraining pipeline demo completed successfully")
        else:
            logger.info("No drift detected, retraining not needed")
            
    except Exception as e:
        logger.error(f"Error in demo: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())