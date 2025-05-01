# TerraFusion Auto-Retraining Pipeline Documentation

## Overview

The TerraFusion auto-retraining pipeline provides automated model monitoring, drift detection, and retraining capabilities for the levy impact prediction model. This system helps ensure that predictive models remain accurate and reliable over time as data patterns evolve.

## Components

The auto-retraining system consists of the following components:

1. **Drift Detector** (`ml/hooks/drift_detector.py`)
   - Monitors model performance and detects when model drift occurs
   - Compares current model metrics with baseline metrics
   - Generates alerts when drift exceeds specified thresholds

2. **Retraining Pipeline** (`ml/training/retrain_pipeline.py`)
   - Handles the end-to-end model retraining process
   - Retrains models when triggered by drift detection
   - Evaluates and saves new models

3. **Retraining Scheduler** (`ml/auto_retraining_scheduler.py`)
   - Schedules periodic drift checks
   - Manages the monitoring and alerting workflow
   - Provides automated execution of the drift detection and retraining process

4. **GitHub Action Workflow** (`.github/workflows/auto_retraining.yml`)
   - Runs the drift detection and retraining process on a schedule
   - Commits updated models to the repository
   - Sends notifications when drift is detected and models are retrained

## Drift Detection

### How Drift Detection Works

The drift detection system monitors two types of drift:

1. **Distribution Drift**: Changes in the statistical distribution of input features
   - Monitors the mean and standard deviation of features
   - Calculates z-scores to detect significant shifts
   - Threshold: 2.0 standard deviations by default

2. **Prediction Drift**: Changes in model prediction error metrics
   - Monitors Mean Squared Error (MSE) and Mean Absolute Error (MAE)
   - Calculates relative changes compared to baseline metrics
   - Threshold: 20% change by default

### Configuring Drift Detection

You can configure the drift detection thresholds and other parameters:

```python
# Initialize drift detector with custom parameters
detector = DriftDetector(
    threshold=3.0,  # For distribution drift (standard deviations)
    model_path='path/to/model.pkl',
    metrics_path='path/to/metrics.json'
)

# For prediction drift, modify the drift_threshold in check_prediction_drift method
# Default is 0.2 (20% change)
```

## Retraining Process

When drift is detected, the retraining pipeline is triggered automatically:

1. The pipeline loads the latest training data
2. It trains a new model using the current best practices
3. The new model is evaluated against the test dataset
4. If the new model performs better, it replaces the existing model
5. Model metrics and artifacts are saved for future drift detection

## Automated Scheduling

### Local Scheduling

You can run the scheduler locally using the RetrainingScheduler class:

```python
from ml.auto_retraining_scheduler import RetrainingScheduler

# Initialize and start the scheduler
scheduler = RetrainingScheduler(
    check_interval_hours=24,  # Check daily
    data_path='data/levy_training_data.csv',
    model_path='ml/models/levy_impact_model.pkl'
)

# Start scheduler
scheduler.start()
```

### GitHub Actions Scheduling

The system is configured to run automatically using GitHub Actions:

- Scheduled to run daily at 3:00 AM UTC
- Can be triggered manually using the workflow_dispatch event
- Commits updated models and creates issues when retraining occurs

## JSON Serialization

The auto-retraining system implements special handling for JSON serialization to ensure compatibility with various tools and systems:

- Boolean values are converted to strings ('True'/'False') to avoid JSON serialization issues
- The `make_json_serializable` utility function handles conversion of complex objects
- All drift detection results are properly serialized before storage or transmission

## Testing the Auto-Retraining System

To test the auto-retraining system:

1. **Run drift detection test**:
   ```
   python ml/test_drift_detection.py
   ```

2. **Run a single drift check**:
   ```
   python ml/auto_retraining_scheduler.py --run-once
   ```

3. **Start the scheduler for continuous monitoring**:
   ```
   python ml/auto_retraining_scheduler.py
   ```

## Monitoring and Logging

The auto-retraining system generates comprehensive logs:

- **Drift check logs**: `logs/drift_checks.json`
- **Retraining logs**: `logs/auto_retraining.log`
- **Notification logs**: `logs/notifications.log`

## Troubleshooting

### Common Issues

1. **Missing model or metrics files**
   - Ensure the model file exists at the specified path
   - Run the initial training if no model exists

2. **JSON serialization errors**
   - Check for non-serializable objects in the results
   - Make sure boolean values are properly converted to strings

3. **No drift detection**
   - Verify that the training data is available
   - Check that metrics.json contains baseline metrics

## Best Practices

1. **Regular monitoring**: Review drift detection logs periodically
2. **Threshold tuning**: Adjust drift thresholds based on domain knowledge
3. **Data quality**: Ensure training data remains high quality
4. **Metrics review**: Regularly review model metrics and performance

## Future Enhancements

- Enhanced notification system with Slack/Email integration
- Multi-model drift detection and retraining
- Advanced drift detection algorithms
- Automated threshold optimization