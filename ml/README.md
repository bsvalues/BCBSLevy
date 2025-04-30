# TerraFusion ML Auto-Retraining Pipeline

This directory contains the ML components of the TerraFusion platform, including auto-retraining capabilities with drift detection.

## Directory Structure

- `training/`: Training pipeline components
  - `retrain_pipeline.py`: Core retraining pipeline for levy impact prediction models
- `hooks/`: Integration points with other systems
  - `drift_detector.py`: Drift detection capabilities for determining when to retrain
- `models/`: Trained model artifacts
  - `levy_impact_model.pkl`: Serialized model for levy impact prediction
  - `model_metrics.json`: Performance metrics for the current model
  - `training_history.csv`: Historical record of training runs
- `retraining_demo.py`: Demonstration script for the auto-retraining pipeline
- `auto_retraining_scheduler.py`: Scheduler for periodic drift checks and retraining

## Auto-Retraining Pipeline

The TerraFusion auto-retraining pipeline provides:

1. **Drift Detection**: Monitors for changes in data distribution or model performance that may indicate the need for retraining.
2. **Automatic Retraining**: Triggers model retraining when drift is detected.
3. **Monitoring & Alerting**: Provides notifications and logs when drift is detected and retraining is performed.
4. **CI/CD Integration**: GitHub Actions workflow for automated drift checks.

## Usage

### Running a Drift Check

```bash
python ml/hooks/drift_detector.py --data-path data/levy_training_data.csv --trigger-retraining
```

### Running the Retraining Demo

```bash
python ml/retraining_demo.py
```

### Starting the Retraining Scheduler

```bash
python ml/auto_retraining_scheduler.py --interval 24
```

## Drift Detection Methods

The system employs multiple drift detection methods:

1. **Distribution Drift**: Analyzes changes in the statistical properties of features
2. **Prediction Drift**: Detects changes in model prediction patterns
3. **Performance Drift**: Monitors degradation in model performance metrics

## CI/CD Integration

The `.github/workflows/auto_retraining.yml` file configures automatic drift checks and retraining via GitHub Actions:

- Scheduled to run daily
- Automatically retrains when drift is detected
- Creates alerts and commits updated models to the repository

## Development

To extend the auto-retraining pipeline:

1. Add new drift detection methods in `hooks/drift_detector.py`
2. Enhance model evaluation in `training/retrain_pipeline.py`
3. Add additional notification channels in `auto_retraining_scheduler.py`