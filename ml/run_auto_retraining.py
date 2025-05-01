#!/usr/bin/env python3
"""
Run script for the TerraFusion auto-retraining pipeline.

This script provides a convenient way to run the TerraFusion auto-retraining
pipeline with various options for demonstration and testing purposes.
"""

import os
import sys
import argparse
import logging
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/run_auto_retraining.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('run_auto_retraining')

def setup_environment():
    """Set up the environment for running the auto-retraining pipeline."""
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Create models directory if it doesn't exist
    os.makedirs('ml/models', exist_ok=True)
    
    # Ensure dummy metrics file exists for testing if needed
    if not os.path.exists('ml/models/model_metrics.json'):
        logger.warning("No model metrics found. Creating dummy metrics file for testing.")
        with open('ml/models/model_metrics.json', 'w') as f:
            f.write('{"mse": 0.05, "mae": 0.15, "r2": 0.85, "timestamp": "' + 
                    datetime.now().isoformat() + '"}')

def run_drift_detection(args):
    """Run the drift detection system."""
    logger.info("Running drift detection...")
    
    try:
        # Import drift detector
        from ml.hooks.drift_detector import DriftDetector, trigger_retraining
        
        # Initialize detector
        detector = DriftDetector(
            model_path=args.model_path,
            metrics_path=args.metrics_path,
            threshold=args.threshold
        )
        
        # Run detector
        result = detector.monitor_and_alert(data_path=args.data_path)
        
        # Print results
        logger.info(f"Drift detection status: {result.get('status', 'unknown')}")
        logger.info(f"Drift detected: {result.get('drift_detected', 'False')}")
        
        # Trigger retraining if requested
        if args.trigger_retraining and result.get('drift_detected') == 'True':
            logger.info("Triggering retraining...")
            retraining_result = trigger_retraining(result)
            logger.info(f"Retraining {'successful' if retraining_result == 'True' else 'failed'}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error running drift detection: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def run_scheduler(args):
    """Run the retraining scheduler."""
    logger.info(f"Running retraining scheduler with interval {args.interval} hours...")
    
    try:
        # Import scheduler
        from ml.auto_retraining_scheduler import RetrainingScheduler
        
        # Initialize scheduler
        scheduler = RetrainingScheduler(
            check_interval_hours=args.interval,
            data_path=args.data_path,
            model_path=args.model_path,
            metrics_path=args.metrics_path
        )
        
        if args.run_once:
            # Run a single check
            logger.info("Running a single drift check...")
            result = scheduler.check_for_drift()
            logger.info(f"Drift check complete: {result.get('status', 'unknown')}")
            return 0
        else:
            # Start scheduler
            logger.info("Starting continuous scheduler...")
            scheduler.start()
            
            # Keep running for specified time or indefinitely
            if args.runtime > 0:
                logger.info(f"Scheduler will run for {args.runtime} minutes")
                end_time = datetime.now() + timedelta(minutes=args.runtime)
                
                while datetime.now() < end_time:
                    time.sleep(1)
                    
                # Stop scheduler
                logger.info("Stopping scheduler...")
                scheduler.stop()
            else:
                logger.info("Scheduler running indefinitely. Press Ctrl+C to stop.")
                try:
                    # Keep the main thread alive
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt received, shutting down...")
                    scheduler.stop()
                    
            return 0
            
    except Exception as e:
        logger.error(f"Error running scheduler: {str(e)}")
        return 1

def main():
    """Main function for processing command line arguments and running chosen mode."""
    parser = argparse.ArgumentParser(
        description='Run the TerraFusion auto-retraining pipeline',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Common arguments
    parser.add_argument('--data-path', default='data/levy_training_data.csv',
                        help='Path to the training data file')
    parser.add_argument('--model-path', default='ml/models/levy_impact_model.pkl',
                        help='Path to the model file')
    parser.add_argument('--metrics-path', default='ml/models/model_metrics.json',
                        help='Path to the model metrics file')
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # Drift detection mode
    drift_parser = subparsers.add_parser('drift', help='Run drift detection')
    drift_parser.add_argument('--threshold', type=float, default=5.0,
                             help='Threshold for drift detection')
    drift_parser.add_argument('--trigger-retraining', action='store_true',
                             help='Trigger retraining if drift is detected')
    
    # Scheduler mode
    scheduler_parser = subparsers.add_parser('scheduler', help='Run retraining scheduler')
    scheduler_parser.add_argument('--interval', type=int, default=24,
                                 help='Check interval in hours')
    scheduler_parser.add_argument('--run-once', action='store_true',
                                 help='Run a single check and exit')
    scheduler_parser.add_argument('--runtime', type=int, default=0,
                                 help='How long to run the scheduler (minutes, 0=indefinitely)')
    
    # Test mode
    test_parser = subparsers.add_parser('test', help='Run auto-retraining tests')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    # Run chosen mode
    if args.mode == 'drift':
        run_drift_detection(args)
        return 0
    elif args.mode == 'scheduler':
        return run_scheduler(args)
    elif args.mode == 'test':
        # Import and run test script
        logger.info("Running auto-retraining tests...")
        from ml.test_drift_detection import main as run_tests
        return run_tests()
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())