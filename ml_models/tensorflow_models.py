"""
TensorFlow models for AgenticAI4DB
Neural networks for database query optimization, performance prediction, and anomaly detection
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import joblib
import json
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set random seeds for reproducibility
tf.random.set_seed(42)
np.random.seed(42)

class QueryPerformancePredictor:
    """
    Deep neural network for predicting SQL query execution time and resource usage
    """
    
    def __init__(self, input_dim: int, hidden_layers: List[int] = [256, 128, 64]):
        self.input_dim = input_dim
        self.hidden_layers = hidden_layers
        self.model = None
        self.history = None
        self.is_trained = False
        
    def build_model(self) -> keras.Model:
        """Build the neural network architecture"""
        model = models.Sequential([
            layers.Input(shape=(self.input_dim,)),
            layers.BatchNormalization(),
        ])
        
        # Add hidden layers with dropout for regularization
        for i, units in enumerate(self.hidden_layers):
            model.add(layers.Dense(
                units,
                activation='relu',
                kernel_regularizer=keras.regularizers.l2(0.001),
                name=f'hidden_{i+1}'
            ))
            model.add(layers.BatchNormalization())
            model.add(layers.Dropout(0.3))
        
        # Output layer for regression (execution time prediction)
        model.add(layers.Dense(1, activation='relu', name='execution_time'))
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        self.model = model
        logger.info(f"Built QueryPerformancePredictor with {model.count_params()} parameters")
        return model
    
    def train(self, 
              X_train: np.ndarray, 
              y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None,
              epochs: int = 100,
              batch_size: int = 32,
              patience: int = 15) -> keras.callbacks.History:
        """Train the model"""
        
        if self.model is None:
            self.build_model()
        
        # Callbacks for training
        callback_list = [
            callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=patience,
                restore_best_weights=True
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=10,
                min_lr=1e-7
            )
        ]
        
        # Prepare validation data
        validation_data = (X_val, y_val) if X_val is not None else None
        
        logger.info(f"Training QueryPerformancePredictor for {epochs} epochs")
        
        # Train the model
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callback_list,
            verbose=1
        )
        
        self.is_trained = True
        logger.info("Training completed successfully")
        return self.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        results = self.model.evaluate(X_test, y_test, verbose=0)
        metrics = {
            'test_loss': results[0],
            'test_mae': results[1],
            'test_mape': results[2]
        }
        
        # Additional custom metrics
        predictions = self.predict(X_test)
        metrics['r2_score'] = self._calculate_r2(y_test, predictions)
        
        return metrics
    
    def _calculate_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate R² score"""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        return r2
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        self.model.save(filepath)
        
        # Save additional metadata
        metadata = {
            'input_dim': self.input_dim,
            'hidden_layers': self.hidden_layers,
            'is_trained': self.is_trained,
            'training_history': self.history.history if self.history else None
        }
        
        metadata_path = filepath.replace('.keras', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        self.model = keras.models.load_model(filepath)
        
        # Load metadata
        metadata_path = filepath.replace('.keras', '_metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            self.input_dim = metadata['input_dim']
            self.hidden_layers = metadata['hidden_layers']
            self.is_trained = metadata['is_trained']
        
        logger.info(f"Model loaded from {filepath}")


class QueryAnomalyDetector:
    """
    Autoencoder-based anomaly detection for SQL queries
    Detects unusual query patterns that might indicate performance issues or security threats
    """
    
    def __init__(self, input_dim: int, encoding_dim: int = 64):
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.autoencoder = None
        self.encoder = None
        self.decoder = None
        self.threshold = None
        self.is_trained = False
    
    def build_model(self) -> Tuple[keras.Model, keras.Model, keras.Model]:
        """Build autoencoder architecture"""
        
        # Encoder
        input_layer = layers.Input(shape=(self.input_dim,))
        encoded = layers.Dense(256, activation='relu')(input_layer)
        encoded = layers.BatchNormalization()(encoded)
        encoded = layers.Dropout(0.2)(encoded)
        encoded = layers.Dense(128, activation='relu')(encoded)
        encoded = layers.BatchNormalization()(encoded)
        encoded = layers.Dropout(0.2)(encoded)
        encoded = layers.Dense(self.encoding_dim, activation='relu', name='encoded')(encoded)
        
        # Decoder
        decoded = layers.Dense(128, activation='relu')(encoded)
        decoded = layers.BatchNormalization()(decoded)
        decoded = layers.Dropout(0.2)(decoded)
        decoded = layers.Dense(256, activation='relu')(decoded)
        decoded = layers.BatchNormalization()(decoded)
        decoded = layers.Dropout(0.2)(decoded)
        decoded = layers.Dense(self.input_dim, activation='sigmoid')(decoded)
        
        # Create models
        self.autoencoder = models.Model(input_layer, decoded)
        self.encoder = models.Model(input_layer, encoded)
        
        # Decoder model
        encoded_input = layers.Input(shape=(self.encoding_dim,))
        decoder_layers = self.autoencoder.layers[-6:]  # Last 6 layers are decoder
        decoder_output = encoded_input
        for layer in decoder_layers:
            decoder_output = layer(decoder_output)
        self.decoder = models.Model(encoded_input, decoder_output)
        
        # Compile autoencoder
        self.autoencoder.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        logger.info(f"Built QueryAnomalyDetector with {self.autoencoder.count_params()} parameters")
        return self.autoencoder, self.encoder, self.decoder
    
    def train(self, 
              X_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              epochs: int = 100,
              batch_size: int = 32,
              patience: int = 15) -> keras.callbacks.History:
        """Train the autoencoder on normal query patterns"""
        
        if self.autoencoder is None:
            self.build_model()
        
        # Normalize input data
        X_train_normalized = self._normalize_data(X_train)
        X_val_normalized = self._normalize_data(X_val) if X_val is not None else None
        
        # Callbacks
        callback_list = [
            callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=patience,
                restore_best_weights=True
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=10
            )
        ]
        
        validation_data = (X_val_normalized, X_val_normalized) if X_val_normalized is not None else None
        
        logger.info(f"Training QueryAnomalyDetector for {epochs} epochs")
        
        # Train autoencoder (input = output for reconstruction)
        history = self.autoencoder.fit(
            X_train_normalized, X_train_normalized,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callback_list,
            verbose=1
        )
        
        # Calculate anomaly threshold based on training data
        train_predictions = self.autoencoder.predict(X_train_normalized, verbose=0)
        train_mse = np.mean(np.power(X_train_normalized - train_predictions, 2), axis=1)
        self.threshold = np.percentile(train_mse, 95)  # 95th percentile as threshold
        
        self.is_trained = True
        logger.info(f"Training completed. Anomaly threshold: {self.threshold:.4f}")
        return history
    
    def detect_anomalies(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Detect anomalies in query patterns"""
        if not self.is_trained:
            raise ValueError("Model must be trained before anomaly detection")
        
        X_normalized = self._normalize_data(X)
        predictions = self.autoencoder.predict(X_normalized, verbose=0)
        
        # Calculate reconstruction error
        mse = np.mean(np.power(X_normalized - predictions, 2), axis=1)
        
        # Classify as anomaly if reconstruction error > threshold
        anomalies = mse > self.threshold
        
        return anomalies, mse
    
    def _normalize_data(self, X: np.ndarray) -> np.ndarray:
        """Normalize data to [0, 1] range"""
        return (X - np.min(X, axis=0)) / (np.max(X, axis=0) - np.min(X, axis=0) + 1e-8)


class QueryClassifier:
    """
    Multi-class neural network classifier for categorizing SQL queries
    Classifies queries by type, complexity, and optimization potential
    """
    
    def __init__(self, input_dim: int, num_classes: int, hidden_layers: List[int] = [128, 64]):
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.hidden_layers = hidden_layers
        self.model = None
        self.is_trained = False
        self.label_encoder = None
    
    def build_model(self) -> keras.Model:
        """Build classification model"""
        model = models.Sequential([
            layers.Input(shape=(self.input_dim,)),
            layers.BatchNormalization(),
        ])
        
        # Hidden layers
        for i, units in enumerate(self.hidden_layers):
            model.add(layers.Dense(
                units,
                activation='relu',
                kernel_regularizer=keras.regularizers.l2(0.001)
            ))
            model.add(layers.BatchNormalization())
            model.add(layers.Dropout(0.4))
        
        # Output layer
        model.add(layers.Dense(self.num_classes, activation='softmax'))
        
        # Compile
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        logger.info(f"Built QueryClassifier with {model.count_params()} parameters")
        return model
    
    def train(self,
              X_train: np.ndarray,
              y_train: np.ndarray,
              X_val: Optional[np.ndarray] = None,
              y_val: Optional[np.ndarray] = None,
              epochs: int = 50,
              batch_size: int = 32) -> keras.callbacks.History:
        """Train the classifier"""
        
        if self.model is None:
            self.build_model()
        
        # Encode labels if they're strings
        if isinstance(y_train[0], str):
            from sklearn.preprocessing import LabelEncoder
            self.label_encoder = LabelEncoder()
            y_train_encoded = self.label_encoder.fit_transform(y_train)
            y_val_encoded = self.label_encoder.transform(y_val) if y_val is not None else None
        else:
            y_train_encoded = y_train
            y_val_encoded = y_val
        
        # Callbacks
        callbacks_list = [
            callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
        ]
        
        validation_data = (X_val, y_val_encoded) if X_val is not None else None
        
        logger.info(f"Training QueryClassifier for {epochs} epochs")
        
        history = self.model.fit(
            X_train, y_train_encoded,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks_list,
            verbose=1
        )
        
        self.is_trained = True
        return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        predictions = self.model.predict(X, verbose=0)
        predicted_classes = np.argmax(predictions, axis=1)
        
        # Decode labels if encoder was used
        if self.label_encoder:
            predicted_classes = self.label_encoder.inverse_transform(predicted_classes)
        
        return predicted_classes
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        return self.model.predict(X, verbose=0)


class DatabaseOptimizationRecommender:
    """
    Advanced neural network for recommending database optimizations
    Uses ensemble of models to suggest schema changes, index recommendations, and query improvements
    """
    
    def __init__(self, feature_dim: int):
        self.feature_dim = feature_dim
        self.performance_predictor = None
        self.anomaly_detector = None
        self.query_classifier = None
        self.recommendation_model = None
        self.is_trained = False
    
    def build_ensemble(self):
        """Build ensemble of models for comprehensive optimization recommendations"""
        
        # Performance prediction branch
        perf_input = layers.Input(shape=(self.feature_dim,), name='perf_input')
        perf_branch = layers.Dense(128, activation='relu')(perf_input)
        perf_branch = layers.BatchNormalization()(perf_branch)
        perf_branch = layers.Dropout(0.3)(perf_branch)
        perf_branch = layers.Dense(64, activation='relu')(perf_branch)
        perf_output = layers.Dense(1, activation='relu', name='performance_score')(perf_branch)
        
        # Query complexity branch
        complexity_branch = layers.Dense(64, activation='relu')(perf_input)
        complexity_branch = layers.BatchNormalization()(complexity_branch)
        complexity_branch = layers.Dropout(0.3)(complexity_branch)
        complexity_output = layers.Dense(1, activation='sigmoid', name='complexity_score')(complexity_branch)
        
        # Optimization potential branch
        opt_branch = layers.Dense(128, activation='relu')(perf_input)
        opt_branch = layers.BatchNormalization()(opt_branch)
        opt_branch = layers.Dropout(0.3)(opt_branch)
        opt_branch = layers.Dense(32, activation='relu')(opt_branch)
        
        # Recommendation categories (multi-label classification)
        # Categories: index_needed, query_rewrite, schema_change, partitioning, caching
        recommendation_output = layers.Dense(5, activation='sigmoid', name='recommendations')(opt_branch)
        
        # Create multi-output model
        self.recommendation_model = models.Model(
            inputs=perf_input,
            outputs=[perf_output, complexity_output, recommendation_output]
        )
        
        # Compile with multiple loss functions
        self.recommendation_model.compile(
            optimizer='adam',
            loss={
                'performance_score': 'mse',
                'complexity_score': 'binary_crossentropy',
                'recommendations': 'binary_crossentropy'
            },
            loss_weights={
                'performance_score': 1.0,
                'complexity_score': 0.5,
                'recommendations': 2.0
            },
            metrics={
                'performance_score': ['mae'],
                'complexity_score': ['accuracy'],
                'recommendations': ['precision', 'recall']
            }
        )
        
        logger.info("Built DatabaseOptimizationRecommender ensemble model")
    
    def train_ensemble(self,
                      X_train: np.ndarray,
                      y_performance: np.ndarray,
                      y_complexity: np.ndarray,
                      y_recommendations: np.ndarray,
                      validation_data: Optional[Tuple] = None,
                      epochs: int = 100,
                      batch_size: int = 32) -> keras.callbacks.History:
        """Train the ensemble model"""
        
        if self.recommendation_model is None:
            self.build_ensemble()
        
        # Prepare training data
        y_train = {
            'performance_score': y_performance,
            'complexity_score': y_complexity,
            'recommendations': y_recommendations
        }
        
        # Callbacks
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10
            )
        ]
        
        logger.info(f"Training ensemble model for {epochs} epochs")
        
        history = self.recommendation_model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks_list,
            verbose=1
        )
        
        self.is_trained = True
        return history
    
    def get_recommendations(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """Get optimization recommendations"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making recommendations")
        
        predictions = self.recommendation_model.predict(X, verbose=0)
        
        # Map recommendation categories
        recommendation_categories = [
            'index_needed',
            'query_rewrite',
            'schema_change',
            'partitioning',
            'caching'
        ]
        
        recommendations = {
            'performance_scores': predictions[0].flatten(),
            'complexity_scores': predictions[1].flatten(),
            'recommendation_probabilities': predictions[2]
        }
        
        # Convert probabilities to binary recommendations (threshold = 0.5)
        for i, category in enumerate(recommendation_categories):
            recommendations[category] = predictions[2][:, i] > 0.5
        
        return recommendations


def create_synthetic_training_data(n_samples: int = 5000) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """
    Create synthetic training data for testing the TensorFlow models
    """
    np.random.seed(42)
    
    # Generate features
    n_features = 30
    X = np.random.randn(n_samples, n_features)
    
    # Add some correlation structure
    X[:, 1] = X[:, 0] + np.random.normal(0, 0.5, n_samples)  # Correlated features
    X[:, 2] = np.abs(X[:, 0]) + np.random.normal(0, 0.3, n_samples)  # Non-linear relationship
    
    # Generate targets
    targets = {}
    
    # Performance scores (execution time)
    targets['performance'] = (
        2 * X[:, 0] + 1.5 * X[:, 1] + 0.8 * X[:, 2] + 
        np.random.normal(0, 0.5, n_samples)
    )
    targets['performance'] = np.maximum(0, targets['performance'])  # Ensure positive
    
    # Query types for classification
    query_weights = np.array([0.3, 0.4, 0.2, 0.1])  # SELECT, INSERT, UPDATE, DELETE
    targets['query_types'] = np.random.choice(4, n_samples, p=query_weights)
    
    # Complexity scores (binary: complex vs simple)
    complexity_prob = 1 / (1 + np.exp(-(X[:, 0] + X[:, 1] - 1)))  # Logistic function
    targets['complexity'] = np.random.binomial(1, complexity_prob, n_samples)
    
    # Multi-label recommendations
    targets['recommendations'] = np.random.binomial(1, 0.3, (n_samples, 5))
    
    logger.info(f"Generated {n_samples} synthetic samples with {n_features} features")
    
    return X, targets


if __name__ == "__main__":
    # Example usage and testing
    logger.info("Testing TensorFlow models for AgenticAI4DB")
    
    # Generate synthetic data
    X_data, y_data = create_synthetic_training_data(1000)
    
    # Split data
    split_idx = int(0.8 * len(X_data))
    X_train, X_test = X_data[:split_idx], X_data[split_idx:]
    
    # Test QueryPerformancePredictor
    logger.info("Testing QueryPerformancePredictor")
    performance_model = QueryPerformancePredictor(input_dim=X_data.shape[1])
    performance_model.build_model()
    
    y_perf_train = y_data['performance'][:split_idx]
    y_perf_test = y_data['performance'][split_idx:]
    
    # Quick training for testing
    performance_model.train(X_train, y_perf_train, epochs=5, batch_size=32)
    
    # Make predictions
    predictions = performance_model.predict(X_test)
    metrics = performance_model.evaluate(X_test, y_perf_test)
    logger.info(f"Performance model metrics: {metrics}")
    
    # Test QueryAnomalyDetector
    logger.info("Testing QueryAnomalyDetector")
    anomaly_model = QueryAnomalyDetector(input_dim=X_data.shape[1])
    anomaly_model.build_model()
    anomaly_model.train(X_train, epochs=5)
    
    anomalies, scores = anomaly_model.detect_anomalies(X_test)
    logger.info(f"Detected {np.sum(anomalies)} anomalies out of {len(X_test)} samples")
    
    # Test QueryClassifier
    logger.info("Testing QueryClassifier")
    classifier = QueryClassifier(input_dim=X_data.shape[1], num_classes=4)
    classifier.build_model()
    
    y_class_train = y_data['query_types'][:split_idx]
    y_class_test = y_data['query_types'][split_idx:]
    
    classifier.train(X_train, y_class_train, epochs=5)
    class_predictions = classifier.predict(X_test)
    logger.info(f"Classification accuracy: {np.mean(class_predictions == y_class_test):.3f}")
    
    logger.info("All TensorFlow models tested successfully!")