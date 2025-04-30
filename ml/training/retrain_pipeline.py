"""
Auto-retraining pipeline for levy impact prediction models.

This module implements the automatic retraining pipeline that periodically
evaluates model performance, detects drift, and triggers retraining when necessary.
It's part of the TerraFusion platform's ML lifecycle management system.
"""

import os
import sys
import logging
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('retrain_pipeline')

class RetrainPipeline:
    """Pipeline for retraining levy impact prediction models."""
    
    def __init__(self, model_path='ml/models/levy_impact_model.pkl'):
        """
        Initialize the retraining pipeline.
        
        Args:
            model_path: Path to the model file
        """
        self.model_path = model_path
        self.metrics_path = os.path.join(os.path.dirname(model_path), 'model_metrics.json')
        self.training_history_path = os.path.join(os.path.dirname(model_path), 'training_history.csv')

    def load_training_data(self, csv_path='data/levy_training_data.csv'):
        """
        Load training data from CSV file.
        
        Args:
            csv_path: Path to the CSV file containing training data
            
        Returns:
            DataFrame containing the training data
        """
        logger.info(f"Loading training data from {csv_path}")
        if not os.path.exists(csv_path):
            logger.error(f"Training data file not found: {csv_path}")
            raise FileNotFoundError(f"Training data file not found: {csv_path}")
            
        return pd.read_csv(csv_path)

    def preprocess_data(self, data):
        """
        Preprocess the training data.
        
        Args:
            data: DataFrame containing the raw training data
            
        Returns:
            X: Feature matrix
            y: Target vector
        """
        logger.info("Preprocessing training data")
        
        # Ensure required columns exist
        required_columns = ['region_encoded', 'forecast']
        for col in required_columns:
            if col not in data.columns:
                logger.error(f"Required column '{col}' not found in training data")
                raise ValueError(f"Required column '{col}' not found in training data")
        
        # Basic feature engineering - in production, this would be more sophisticated
        X = data[['region_encoded']]
        
        # Add additional features if available
        additional_features = ['year', 'previous_value', 'growth_rate']
        for feat in additional_features:
            if feat in data.columns:
                X[feat] = data[feat]
        
        y = data['forecast']
        
        return X, y

    def train_model(self, X, y, model_type='linear'):
        """
        Train a prediction model.
        
        Args:
            X: Feature matrix
            y: Target vector
            model_type: Type of model to train ('linear' or 'forest')
            
        Returns:
            Trained model instance
        """
        logger.info(f"Training {model_type} regression model")
        
        if model_type == 'linear':
            model = LinearRegression()
        elif model_type == 'forest':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            logger.error(f"Unknown model type: {model_type}")
            raise ValueError(f"Unknown model type: {model_type}")
        
        model.fit(X, y)
        return model

    def evaluate_model(self, model, X, y):
        """
        Evaluate model performance.
        
        Args:
            model: Trained model instance
            X: Feature matrix
            y: Target vector
            
        Returns:
            Dictionary containing evaluation metrics
        """
        logger.info("Evaluating model performance")
        
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y, y_pred)
        
        metrics = {
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Model metrics: MSE={mse:.4f}, RMSE={rmse:.4f}, R²={r2:.4f}")
        return metrics

    def save_model(self, model, metrics):
        """
        Save the trained model and its metrics.
        
        Args:
            model: Trained model instance
            metrics: Dictionary containing evaluation metrics
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Save model
        logger.info(f"Saving model to {self.model_path}")
        joblib.dump(model, self.model_path)
        
        # Save metrics
        import json
        with open(self.metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Append to training history
        metrics_df = pd.DataFrame([metrics])
        if os.path.exists(self.training_history_path):
            history_df = pd.read_csv(self.training_history_path)
            history_df = pd.concat([history_df, metrics_df], ignore_index=True)
        else:
            history_df = metrics_df
        
        history_df.to_csv(self.training_history_path, index=False)
        logger.info("Model and metrics saved successfully")

    def run(self, csv_path='data/levy_training_data.csv', model_type='linear'):
        """
        Run the full retraining pipeline.
        
        Args:
            csv_path: Path to the CSV file containing training data
            model_type: Type of model to train ('linear' or 'forest')
            
        Returns:
            Dictionary containing evaluation metrics
        """
        logger.info("Starting model retraining pipeline")
        
        try:
            # Load and preprocess data
            data = self.load_training_data(csv_path)
            X, y = self.preprocess_data(data)
            
            # Train model
            model = self.train_model(X, y, model_type)
            
            # Evaluate model
            metrics = self.evaluate_model(model, X, y)
            
            # Save model and metrics
            self.save_model(model, metrics)
            
            logger.info("Model retraining completed successfully")
            return metrics
            
        except Exception as e:
            logger.error(f"Error in retraining pipeline: {str(e)}")
            raise

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Retrain levy impact prediction model')
    parser.add_argument('--data', default='data/levy_training_data.csv', help='Path to training data CSV')
    parser.add_argument('--model-type', default='linear', choices=['linear', 'forest'], help='Type of model to train')
    parser.add_argument('--model-path', default='ml/models/levy_impact_model.pkl', help='Path to save the model')
    args = parser.parse_args()
    
    # Run retraining pipeline
    pipeline = RetrainPipeline(model_path=args.model_path)
    try:
        metrics = pipeline.run(csv_path=args.data, model_type=args.model_type)
        print(f"Model successfully trained and saved to {args.model_path}")
        print(f"Performance: MSE={metrics['mse']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)