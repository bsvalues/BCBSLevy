"""
Model drift detection for TerraFusion ML models.

This module implements drift detection capabilities to determine when
a model's performance is degrading due to data distribution changes or
other factors that might require retraining.
"""

import os
import sys
import logging
import numpy as np
import pandas as pd
import joblib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('drift_detector')

class DriftDetector:
    """Detects drift in model performance or data distribution."""
    
    def __init__(self, 
                 baseline_mean: Optional[float] = None, 
                 threshold: float = 5.0,
                 model_path: str = 'ml/models/levy_impact_model.pkl',
                 metrics_path: str = 'ml/models/model_metrics.json',
                 window_size: int = 30):
        """
        Initialize the drift detector.
        
        Args:
            baseline_mean: Baseline mean value for comparison
            threshold: Threshold for determining drift
            model_path: Path to the model file
            metrics_path: Path to the model metrics file
            window_size: Number of data points to use for drift detection
        """
        self.baseline_mean = baseline_mean
        self.threshold = threshold
        self.model_path = model_path
        self.metrics_path = metrics_path
        self.window_size = window_size
        self.metrics_history = []
        self.prediction_history = []
        
        # Try to load metrics from file if available
        if os.path.exists(metrics_path):
            self._load_metrics()
        
    def _load_metrics(self):
        """Load metrics from the metrics file."""
        try:
            with open(self.metrics_path, 'r') as f:
                metrics = json.load(f)
                
            # If baseline mean wasn't provided, use the one from metrics
            if self.baseline_mean is None and 'baseline_mean' in metrics:
                self.baseline_mean = metrics['baseline_mean']
                logger.info(f"Loaded baseline mean from metrics: {self.baseline_mean}")
                
        except Exception as e:
            logger.error(f"Error loading metrics from {self.metrics_path}: {str(e)}")

    def check_value_drift(self, new_value: float) -> Tuple[bool, float]:
        """
        Check if a single value indicates drift.
        
        Args:
            new_value: New value to check
            
        Returns:
            Tuple of (drift_detected, drift_magnitude)
        """
        if self.baseline_mean is None:
            logger.warning("No baseline mean available for comparison")
            return False, 0.0
            
        drift = abs(new_value - self.baseline_mean)
        drift_detected = drift > self.threshold
        
        if drift_detected:
            logger.warning(f"Drift detected: value={new_value}, "
                          f"baseline={self.baseline_mean}, drift={drift}")
        
        return drift_detected, drift

    def check_distribution_drift(self, 
                               new_data: pd.DataFrame, 
                               reference_data: Optional[pd.DataFrame] = None,
                               feature_cols: Optional[List[str]] = None
                               ) -> Dict[str, Any]:
        """
        Check for drift in data distribution.
        
        Args:
            new_data: New data to check for drift
            reference_data: Reference data for comparison
            feature_cols: List of feature columns to check
            
        Returns:
            Dictionary containing drift metrics
        """
        if feature_cols is None:
            # Default feature columns
            feature_cols = ['region_encoded']
            # Add extra columns if they exist
            for col in ['year', 'previous_value', 'growth_rate']:
                if col in new_data.columns:
                    feature_cols.append(col)
        
        # If no reference data is provided, try to load training data
        if reference_data is None:
            try:
                reference_data = pd.read_csv('data/levy_training_data.csv')
            except Exception as e:
                logger.error(f"Error loading reference data: {str(e)}")
                return {'drift_detected': False, 'error': str(e)}
        
        result = {
            'drift_detected': False,
            'features': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check drift for each feature
        for col in feature_cols:
            if col not in new_data.columns or col not in reference_data.columns:
                continue
                
            # Basic statistics comparison
            ref_mean = reference_data[col].mean()
            ref_std = reference_data[col].std()
            new_mean = new_data[col].mean()
            new_std = new_data[col].std()
            
            # Calculate z-score of the new mean relative to reference distribution
            z_score = abs(new_mean - ref_mean) / (ref_std if ref_std > 0 else 1.0)
            
            # Drift threshold (2 standard deviations by default)
            drift_threshold = 2.0
            drift_detected = z_score > drift_threshold
            
            # Store results
            result['features'][col] = {
                'reference_mean': ref_mean,
                'reference_std': ref_std,
                'current_mean': new_mean,
                'current_std': new_std,
                'z_score': z_score,
                'drift_detected': drift_detected
            }
            
            # Mark overall drift if any feature has drift
            if drift_detected:
                result['drift_detected'] = True
                logger.warning(f"Drift detected in feature '{col}': "
                             f"z-score={z_score:.2f}, threshold={drift_threshold}")
        
        return result

    def check_prediction_drift(self, 
                             model, 
                             new_data: pd.DataFrame, 
                             target_col: str = 'forecast'
                             ) -> Dict[str, Any]:
        """
        Check for drift in model predictions.
        
        Args:
            model: Model to use for predictions
            new_data: New data to check for drift
            target_col: Name of the target column
            
        Returns:
            Dictionary containing drift metrics
        """
        if target_col not in new_data.columns:
            logger.error(f"Target column '{target_col}' not found in data")
            return {'drift_detected': False, 'error': f"Target column '{target_col}' not found"}
        
        # Extract features and target
        features = []
        for col in new_data.columns:
            if col != target_col:
                features.append(col)
        
        X = new_data[features]
        y_true = new_data[target_col]
        
        # Make predictions
        y_pred = model.predict(X)
        
        # Calculate metrics
        residuals = y_true - y_pred
        mse = np.mean(residuals ** 2)
        mae = np.mean(np.abs(residuals))
        
        # Load reference metrics if available
        ref_mse = None
        ref_mae = None
        if os.path.exists(self.metrics_path):
            try:
                with open(self.metrics_path, 'r') as f:
                    metrics = json.load(f)
                ref_mse = metrics.get('mse')
                ref_mae = metrics.get('mae', metrics.get('mse'))  # Fallback to MSE
            except Exception as e:
                logger.error(f"Error loading reference metrics: {str(e)}")
        
        # If no reference metrics, can't determine drift
        if ref_mse is None:
            logger.warning("No reference metrics available, can't determine prediction drift")
            return {
                'drift_detected': False,
                'current_mse': mse,
                'current_mae': mae,
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate relative change in metrics
        mse_change = (mse - ref_mse) / ref_mse
        mae_change = (mae - ref_mae) / ref_mae
        
        # Drift thresholds (20% by default)
        drift_threshold = 0.2
        drift_detected = mse_change > drift_threshold or mae_change > drift_threshold
        
        result = {
            'drift_detected': drift_detected,
            'reference_mse': ref_mse,
            'reference_mae': ref_mae,
            'current_mse': mse,
            'current_mae': mae,
            'mse_change': mse_change,
            'mae_change': mae_change,
            'timestamp': datetime.now().isoformat()
        }
        
        if drift_detected:
            logger.warning(f"Prediction drift detected: "
                         f"MSE change={mse_change:.2%}, MAE change={mae_change:.2%}")
        
        return result

    def monitor_and_alert(self, 
                        data_path: str = 'data/levy_training_data.csv',
                        alert_callback: Optional[Callable] = None,
                        check_interval_days: int = 7
                        ) -> Dict[str, Any]:
        """
        Monitor for drift and trigger alerts if detected.
        
        Args:
            data_path: Path to the data file
            alert_callback: Function to call if drift is detected
            check_interval_days: Number of days between checks
            
        Returns:
            Dictionary containing monitoring results
        """
        try:
            # Load model and data
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found: {self.model_path}")
                return {'status': 'error', 'message': f"Model file not found: {self.model_path}"}
                
            if not os.path.exists(data_path):
                logger.error(f"Data file not found: {data_path}")
                return {'status': 'error', 'message': f"Data file not found: {data_path}"}
                
            model = joblib.load(self.model_path)
            data = pd.read_csv(data_path)
            
            # Check for drift
            distribution_drift = self.check_distribution_drift(data)
            prediction_drift = self.check_prediction_drift(model, data)
            
            # Combine results
            drift_detected = distribution_drift['drift_detected'] or prediction_drift['drift_detected']
            
            result = {
                'status': 'alert' if drift_detected else 'ok',
                'drift_detected': drift_detected,
                'distribution_drift': distribution_drift,
                'prediction_drift': prediction_drift,
                'timestamp': datetime.now().isoformat(),
                'next_check': (datetime.now() + pd.Timedelta(days=check_interval_days)).isoformat()
            }
            
            # Call alert callback if drift is detected
            if drift_detected and alert_callback is not None:
                alert_callback(result)
                
            return result
            
        except Exception as e:
            logger.error(f"Error in drift monitoring: {str(e)}")
            return {'status': 'error', 'message': str(e)}

def trigger_retraining(drift_result: Dict[str, Any]) -> bool:
    """
    Trigger model retraining based on drift detection results.
    
    Args:
        drift_result: Dictionary containing drift detection results
        
    Returns:
        True if retraining was triggered, False otherwise
    """
    if not drift_result.get('drift_detected', False):
        logger.info("No drift detected, retraining not needed")
        return False
        
    logger.info("Drift detected, triggering retraining")
    
    try:
        # Import here to avoid circular imports
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from training.retrain_pipeline import RetrainPipeline
        
        # Run retraining
        pipeline = RetrainPipeline()
        metrics = pipeline.run()
        
        logger.info(f"Retraining completed successfully: MSE={metrics['mse']:.4f}")
        return True
        
    except Exception as e:
        logger.error(f"Error triggering retraining: {str(e)}")
        return False

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Detect drift in model performance')
    parser.add_argument('--model-path', default='ml/models/levy_impact_model.pkl', help='Path to the model file')
    parser.add_argument('--data-path', default='data/levy_training_data.csv', help='Path to the data file')
    parser.add_argument('--baseline-mean', type=float, help='Baseline mean value for comparison')
    parser.add_argument('--threshold', type=float, default=5.0, help='Threshold for determining drift')
    parser.add_argument('--trigger-retraining', action='store_true', help='Trigger retraining if drift is detected')
    args = parser.parse_args()
    
    # Create drift detector
    detector = DriftDetector(
        baseline_mean=args.baseline_mean,
        threshold=args.threshold,
        model_path=args.model_path
    )
    
    # Run monitoring
    try:
        result = detector.monitor_and_alert(data_path=args.data_path)
        
        # Print results
        print(f"Drift detection status: {result['status']}")
        print(f"Drift detected: {result['drift_detected']}")
        
        # Trigger retraining if requested and drift detected
        if args.trigger_retraining and result['drift_detected']:
            print("Triggering retraining...")
            retraining_success = trigger_retraining(result)
            print(f"Retraining {'successful' if retraining_success else 'failed'}")
            
        sys.exit(0 if result['status'] != 'error' else 1)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)