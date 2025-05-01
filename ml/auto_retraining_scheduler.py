"""
Scheduler for the TerraFusion auto-retraining pipeline.

This script provides a framework for scheduling regular checks for model drift
and triggering retraining when necessary. It integrates with monitoring systems
to provide alerts and logs when drift is detected and retraining is performed.
"""

import os
import sys
import logging
import time
import json
import argparse
from datetime import datetime, timedelta
import signal
import threading
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_retraining.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('auto_retraining_scheduler')

def make_json_serializable(obj: Any) -> Any:
    """
    Convert any Python object to a JSON-serializable type.
    
    Args:
        obj: Any Python object
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(x) for x in obj]
    elif isinstance(obj, (int, float, str, type(None))):
        return obj
    elif isinstance(obj, bool):
        return str(obj)  # Convert bools to strings
    else:
        return str(obj)  # Convert anything else to string

class RetrainingScheduler:
    """Scheduler for periodic drift detection and model retraining."""
    
    def __init__(self, 
                 check_interval_hours: int = 24,
                 data_path: str = 'data/levy_training_data.csv',
                 model_path: str = 'ml/models/levy_impact_model.pkl',
                 metrics_path: str = 'ml/models/model_metrics.json'):
        """
        Initialize the retraining scheduler.
        
        Args:
            check_interval_hours: Hours between drift checks
            data_path: Path to the data file
            model_path: Path to the model file
            metrics_path: Path to the model metrics file
        """
        self.check_interval_hours = check_interval_hours
        self.data_path = data_path
        self.model_path = model_path
        self.metrics_path = metrics_path
        self.running = False
        self.last_check_time = None
        self.next_check_time = None
        self.scheduler_thread = None
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Create an event to signal the scheduler to exit
        self.stop_event = threading.Event()
    
    def _send_notification(self, subject: str, message: str):
        """
        Send a notification about retraining or drift detection.
        
        In a real system, this would integrate with email, Slack, or other
        notification services.
        
        Args:
            subject: Notification subject
            message: Notification message
        """
        logger.info(f"NOTIFICATION: {subject}\n{message}")
        
        # In a production system, you could add integrations here:
        # - Email notifications
        # - Slack messages
        # - Webhooks to other systems
        # - Monitoring system alerts
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # For now, we'll just write to a notifications log file
        with open('logs/notifications.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {subject}: {message}\n")
    
    def check_for_drift(self) -> Dict[str, Any]:
        """
        Check for model drift and trigger retraining if necessary.
        
        Returns:
            Dictionary containing check results
        """
        logger.info("Checking for model drift")
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        try:
            # Import here to avoid circular imports
            from hooks.drift_detector import DriftDetector, trigger_retraining
            
            # Create drift detector
            detector = DriftDetector(model_path=self.model_path, metrics_path=self.metrics_path)
            
            # Run monitoring
            result = detector.monitor_and_alert(data_path=self.data_path)
            
            # If drift detected, trigger retraining
            if result.get('drift_detected', False):
                logger.warning("Drift detected, triggering retraining")
                
                # Send notification
                self._send_notification(
                    "Model Drift Detected", 
                    f"Drift detected in levy impact prediction model. Retraining initiated.\n"
                    f"Drift details: {json.dumps(make_json_serializable(result), indent=2)}"
                )
                
                # Trigger retraining
                try:
                    retraining_success = trigger_retraining(result)
                    
                    if retraining_success == "True":
                        logger.info("Retraining completed successfully")
                        self._send_notification(
                            "Model Retraining Complete",
                            "Levy impact prediction model has been successfully retrained."
                        )
                    else:
                        logger.error("Retraining failed")
                        self._send_notification(
                            "Model Retraining Failed",
                            "Attempt to retrain levy impact prediction model failed."
                        )
                    
                    result['retraining_triggered'] = "True"
                    result['retraining_success'] = retraining_success  # Already a string from trigger_retraining
                except Exception as e:
                    logger.error(f"Error in retraining: {str(e)}")
                    result['retraining_triggered'] = "True"
                    result['retraining_success'] = "False"
                    result['retraining_error'] = str(e)
            else:
                logger.info("No drift detected, model is performing well")
                result['retraining_triggered'] = "False"
            
            # Update check timestamps
            self.last_check_time = datetime.now()
            self.next_check_time = self.last_check_time + timedelta(hours=self.check_interval_hours)
            
            # Add timestamps to result
            result['last_check_time'] = self.last_check_time.isoformat()
            result['next_check_time'] = self.next_check_time.isoformat()
            
            # Save check results to log
            try:
                # Use the global serialization function
                serializable_result = make_json_serializable(result)
                
                with open('logs/drift_checks.json', 'a') as f:
                    f.write(json.dumps(serializable_result) + '\n')
            except Exception as e:
                logger.error(f"Error saving drift check results: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking for drift: {str(e)}")
            
            error_result = {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save check results to log even if there was an error
            serializable_error = make_json_serializable(error_result)
            with open('logs/drift_checks.json', 'a') as f:
                f.write(json.dumps(serializable_error) + '\n')
            
            return error_result
    
    def _scheduler_loop(self):
        """Run the scheduler loop in a separate thread."""
        logger.info(f"Starting scheduler loop with check interval of {self.check_interval_hours} hours")
        
        while not self.stop_event.is_set():
            try:
                # Run initial check
                self.check_for_drift()
                
                # Calculate seconds until next check
                now = datetime.now()
                next_check = now + timedelta(hours=self.check_interval_hours)
                seconds_to_next_check = (next_check - now).total_seconds()
                
                logger.info(f"Next check scheduled for {next_check.isoformat()} "
                          f"({seconds_to_next_check:.1f} seconds from now)")
                
                # Wait until next check, but check stop_event every 10 seconds
                for _ in range(int(seconds_to_next_check / 10)):
                    if self.stop_event.is_set():
                        break
                    time.sleep(10)
                
                # If there's a remainder less than 10 seconds, wait that long
                remainder = seconds_to_next_check % 10
                if remainder > 0 and not self.stop_event.is_set():
                    time.sleep(remainder)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying
    
    def start(self):
        """Start the scheduler."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting retraining scheduler")
        self.running = True
        self.stop_event.clear()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping retraining scheduler")
        self.running = False
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
    
    def _signal_handler(self, sig, frame):
        """Handle signals for graceful shutdown."""
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
        sys.exit(0)

def main():
    """Main function for running the scheduler as a standalone script."""
    parser = argparse.ArgumentParser(description='Schedule periodic model drift checks and retraining')
    parser.add_argument('--interval', type=int, default=24, help='Check interval in hours')
    parser.add_argument('--data-path', default='data/levy_training_data.csv', help='Path to the data file')
    parser.add_argument('--model-path', default='ml/models/levy_impact_model.pkl', help='Path to the model file')
    parser.add_argument('--run-once', action='store_true', help='Run a single check and exit')
    args = parser.parse_args()
    
    try:
        if args.run_once:
            # Create scheduler but just run a single check
            scheduler = RetrainingScheduler(
                check_interval_hours=args.interval,
                data_path=args.data_path,
                model_path=args.model_path
            )
            result = scheduler.check_for_drift()
            
            # Use the global utility function to create a serializable version for printing
            serializable_result = make_json_serializable(result)
            print(json.dumps(serializable_result, indent=2))
            return 0
        else:
            # Start scheduler and run indefinitely
            scheduler = RetrainingScheduler(
                check_interval_hours=args.interval,
                data_path=args.data_path,
                model_path=args.model_path
            )
            scheduler.start()
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        if 'scheduler' in locals():
            scheduler.stop()
        return 0
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())