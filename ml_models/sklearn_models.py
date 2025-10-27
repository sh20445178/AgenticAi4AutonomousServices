"""
Scikit-learn models for AgenticAI4DB
Traditional machine learning models for database optimization and analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.ensemble import (
    RandomForestRegressor, RandomForestClassifier,
    GradientBoostingRegressor, GradientBoostingClassifier,
    VotingRegressor, VotingClassifier
)
from sklearn.svm import SVR, SVC
from sklearn.linear_model import (
    LinearRegression, LogisticRegression, Ridge, Lasso, ElasticNet
)
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
from sklearn.model_selection import (
    cross_val_score, GridSearchCV, RandomizedSearchCV, 
    train_test_split, StratifiedKFold, KFold
)
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    classification_report, confusion_matrix, silhouette_score,
    accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_regression, f_classif, RFE
from sklearn.pipeline import Pipeline
import joblib
import json
import logging
from datetime import datetime
import warnings

# Suppress sklearn warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryPerformanceRegressor:
    """
    Ensemble of regression models for predicting SQL query execution time
    """
    
    def __init__(self):
        self.models = {}
        self.ensemble = None
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.is_trained = False
        self.best_model_name = None
        self.cv_scores = {}
        
    def initialize_models(self):
        """Initialize various regression models"""
        self.models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                min_samples_split=5,
                random_state=42
            ),
            'svr': SVR(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                epsilon=0.1
            ),
            'ridge': Ridge(
                alpha=1.0,
                random_state=42
            ),
            'lasso': Lasso(
                alpha=0.1,
                random_state=42,
                max_iter=2000
            ),
            'elastic_net': ElasticNet(
                alpha=0.1,
                l1_ratio=0.5,
                random_state=42,
                max_iter=2000
            ),
            'linear_regression': LinearRegression(),
            'decision_tree': DecisionTreeRegressor(
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        }
        
        logger.info(f"Initialized {len(self.models)} regression models")
    
    def train_and_evaluate(self, 
                          X_train: np.ndarray, 
                          y_train: np.ndarray,
                          X_test: np.ndarray,
                          y_test: np.ndarray,
                          n_features: int = None,
                          cv_folds: int = 5) -> Dict[str, Dict[str, float]]:
        """Train all models and evaluate performance"""
        
        if not self.models:
            self.initialize_models()
        
        # Feature scaling
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Feature selection if specified
        if n_features and n_features < X_train.shape[1]:
            self.feature_selector = SelectKBest(score_func=f_regression, k=n_features)
            X_train_scaled = self.feature_selector.fit_transform(X_train_scaled, y_train)
            X_test_scaled = self.feature_selector.transform(X_test_scaled)
            logger.info(f"Selected top {n_features} features")
        
        results = {}
        trained_models = {}
        
        # Train and evaluate each model
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            
            try:
                # Cross-validation
                cv_scores = cross_val_score(
                    model, X_train_scaled, y_train, 
                    cv=cv_folds, scoring='neg_mean_squared_error', n_jobs=-1
                )
                self.cv_scores[name] = -cv_scores.mean()
                
                # Train on full training set
                model.fit(X_train_scaled, y_train)
                trained_models[name] = model
                
                # Make predictions
                y_pred_train = model.predict(X_train_scaled)
                y_pred_test = model.predict(X_test_scaled)
                
                # Calculate metrics
                results[name] = {
                    'train_mse': mean_squared_error(y_train, y_pred_train),
                    'test_mse': mean_squared_error(y_test, y_pred_test),
                    'train_mae': mean_absolute_error(y_train, y_pred_train),
                    'test_mae': mean_absolute_error(y_test, y_pred_test),
                    'train_r2': r2_score(y_train, y_pred_train),
                    'test_r2': r2_score(y_test, y_pred_test),
                    'cv_mse': self.cv_scores[name]
                }
                
                logger.info(f"{name} - Test R²: {results[name]['test_r2']:.4f}, "
                           f"Test MSE: {results[name]['test_mse']:.4f}")
                
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
                results[name] = {'error': str(e)}
        
        # Find best model based on CV score
        valid_models = {k: v for k, v in self.cv_scores.items() if k in trained_models}
        if valid_models:
            self.best_model_name = min(valid_models, key=valid_models.get)
            logger.info(f"Best model: {self.best_model_name} (CV MSE: {valid_models[self.best_model_name]:.4f})")
        
        self.models = trained_models
        self.is_trained = True
        
        return results
    
    def create_ensemble(self, top_n: int = 3) -> VotingRegressor:
        """Create voting ensemble from top performing models"""
        if not self.is_trained:
            raise ValueError("Models must be trained before creating ensemble")
        
        # Get top N models based on CV scores
        sorted_models = sorted(self.cv_scores.items(), key=lambda x: x[1])[:top_n]
        
        ensemble_models = []
        for name, _ in sorted_models:
            if name in self.models:
                ensemble_models.append((name, self.models[name]))
        
        if len(ensemble_models) < 2:
            logger.warning("Not enough models for ensemble, using best single model")
            return self.models[self.best_model_name]
        
        self.ensemble = VotingRegressor(estimators=ensemble_models)
        logger.info(f"Created ensemble with {len(ensemble_models)} models: {[name for name, _ in ensemble_models]}")
        
        return self.ensemble
    
    def predict(self, X: np.ndarray, use_ensemble: bool = True) -> np.ndarray:
        """Make predictions using best model or ensemble"""
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Apply feature selection if used
        if self.feature_selector:
            X_scaled = self.feature_selector.transform(X_scaled)
        
        if use_ensemble and self.ensemble:
            return self.ensemble.predict(X_scaled)
        else:
            return self.models[self.best_model_name].predict(X_scaled)
    
    def get_feature_importance(self) -> Dict[str, np.ndarray]:
        """Get feature importance from tree-based models"""
        importance_dict = {}
        
        tree_models = ['random_forest', 'gradient_boosting', 'decision_tree']
        
        for name in tree_models:
            if name in self.models and hasattr(self.models[name], 'feature_importances_'):
                importance_dict[name] = self.models[name].feature_importances_
        
        return importance_dict


class QueryClassificationSuite:
    """
    Multi-class classification models for SQL query categorization
    """
    
    def __init__(self):
        self.models = {}
        self.ensemble = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.best_model_name = None
        self.classification_results = {}
    
    def initialize_models(self):
        """Initialize classification models"""
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'svc': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=2000,
                multi_class='ovr'
            ),
            'decision_tree': DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        }
        
        logger.info(f"Initialized {len(self.models)} classification models")
    
    def train_and_evaluate(self,
                          X_train: np.ndarray,
                          y_train: np.ndarray,
                          X_test: np.ndarray,
                          y_test: np.ndarray,
                          cv_folds: int = 5) -> Dict[str, Dict[str, Any]]:
        """Train and evaluate classification models"""
        
        if not self.models:
            self.initialize_models()
        
        # Encode labels if they're strings
        if isinstance(y_train[0], str):
            y_train_encoded = self.label_encoder.fit_transform(y_train)
            y_test_encoded = self.label_encoder.transform(y_test)
        else:
            y_train_encoded = y_train
            y_test_encoded = y_test
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        trained_models = {}
        cv_scores = {}
        
        for name, model in self.models.items():
            logger.info(f"Training classifier {name}...")
            
            try:
                # Cross-validation
                cv_score = cross_val_score(
                    model, X_train_scaled, y_train_encoded,
                    cv=StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42),
                    scoring='accuracy', n_jobs=-1
                )
                cv_scores[name] = cv_score.mean()
                
                # Train model
                model.fit(X_train_scaled, y_train_encoded)
                trained_models[name] = model
                
                # Predictions
                y_pred_train = model.predict(X_train_scaled)
                y_pred_test = model.predict(X_test_scaled)
                
                # Calculate metrics
                results[name] = {
                    'train_accuracy': accuracy_score(y_train_encoded, y_pred_train),
                    'test_accuracy': accuracy_score(y_test_encoded, y_pred_test),
                    'train_precision': precision_score(y_train_encoded, y_pred_train, average='weighted'),
                    'test_precision': precision_score(y_test_encoded, y_pred_test, average='weighted'),
                    'train_recall': recall_score(y_train_encoded, y_pred_train, average='weighted'),
                    'test_recall': recall_score(y_test_encoded, y_pred_test, average='weighted'),
                    'train_f1': f1_score(y_train_encoded, y_pred_train, average='weighted'),
                    'test_f1': f1_score(y_test_encoded, y_pred_test, average='weighted'),
                    'cv_accuracy': cv_scores[name],
                    'classification_report': classification_report(
                        y_test_encoded, y_pred_test, 
                        target_names=self.label_encoder.classes_ if hasattr(self, 'label_encoder') else None,
                        output_dict=True
                    )
                }
                
                logger.info(f"{name} - Test Accuracy: {results[name]['test_accuracy']:.4f}, "
                           f"Test F1: {results[name]['test_f1']:.4f}")
                
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
                results[name] = {'error': str(e)}
        
        # Find best model
        valid_scores = {k: v for k, v in cv_scores.items() if k in trained_models}
        if valid_scores:
            self.best_model_name = max(valid_scores, key=valid_scores.get)
            logger.info(f"Best classifier: {self.best_model_name} (CV Accuracy: {valid_scores[self.best_model_name]:.4f})")
        
        self.models = trained_models
        self.classification_results = results
        self.is_trained = True
        
        return results


class DatabaseClusterAnalyzer:
    """
    Unsupervised learning for database pattern analysis and clustering
    """
    
    def __init__(self):
        self.clustering_models = {}
        self.dimensionality_reducers = {}
        self.scaler = StandardScaler()
        self.cluster_labels = None
        self.cluster_metrics = {}
        
    def initialize_clustering_models(self, n_clusters: int = 5):
        """Initialize clustering models"""
        self.clustering_models = {
            'kmeans': KMeans(
                n_clusters=n_clusters,
                random_state=42,
                n_init=10
            ),
            'dbscan': DBSCAN(
                eps=0.5,
                min_samples=5
            ),
            'agglomerative': AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage='ward'
            )
        }
        
        self.dimensionality_reducers = {
            'pca': PCA(n_components=min(50, n_clusters * 10), random_state=42),
            'truncated_svd': TruncatedSVD(n_components=min(50, n_clusters * 10), random_state=42),
            'tsne': TSNE(n_components=2, random_state=42, perplexity=30)
        }
        
        logger.info(f"Initialized clustering models for {n_clusters} clusters")
    
    def analyze_clusters(self, X: np.ndarray, n_clusters_range: Tuple[int, int] = (2, 10)) -> Dict[str, Any]:
        """Perform comprehensive cluster analysis"""
        
        # Scale the data
        X_scaled = self.scaler.fit_transform(X)
        
        results = {
            'clustering_results': {},
            'optimal_clusters': {},
            'dimensionality_reduction': {},
            'cluster_metrics': {}
        }
        
        # Find optimal number of clusters for K-means
        logger.info("Finding optimal number of clusters...")
        inertias = []
        silhouette_scores = []
        k_range = range(n_clusters_range[0], n_clusters_range[1] + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            inertias.append(kmeans.inertia_)
            if len(set(cluster_labels)) > 1:  # Need at least 2 clusters for silhouette
                silhouette_scores.append(silhouette_score(X_scaled, cluster_labels))
            else:
                silhouette_scores.append(-1)
        
        # Find elbow point (simplified)
        optimal_k = k_range[np.argmax(silhouette_scores)]
        results['optimal_clusters']['kmeans'] = optimal_k
        
        logger.info(f"Optimal number of clusters (K-means): {optimal_k}")
        
        # Initialize models with optimal parameters
        self.initialize_clustering_models(optimal_k)
        
        # Perform clustering with each algorithm
        for name, model in self.clustering_models.items():
            logger.info(f"Performing {name} clustering...")
            
            try:
                if name == 'dbscan':
                    # DBSCAN doesn't need n_clusters
                    cluster_labels = model.fit_predict(X_scaled)
                else:
                    cluster_labels = model.fit_predict(X_scaled)
                
                n_clusters_found = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
                
                results['clustering_results'][name] = {
                    'labels': cluster_labels,
                    'n_clusters': n_clusters_found,
                    'n_noise': list(cluster_labels).count(-1) if -1 in cluster_labels else 0
                }
                
                # Calculate silhouette score if valid clustering
                if n_clusters_found > 1:
                    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
                    results['cluster_metrics'][name] = {
                        'silhouette_score': silhouette_avg,
                        'n_clusters': n_clusters_found
                    }
                else:
                    results['cluster_metrics'][name] = {
                        'silhouette_score': -1,
                        'n_clusters': n_clusters_found
                    }
                
                logger.info(f"{name} found {n_clusters_found} clusters, "
                           f"Silhouette score: {results['cluster_metrics'][name]['silhouette_score']:.4f}")
                
            except Exception as e:
                logger.error(f"Error in {name} clustering: {str(e)}")
                results['clustering_results'][name] = {'error': str(e)}
        
        # Dimensionality reduction
        for name, reducer in self.dimensionality_reducers.items():
            logger.info(f"Performing {name} dimensionality reduction...")
            
            try:
                if name == 'tsne':
                    # t-SNE is computationally expensive, use subset for large datasets
                    sample_size = min(1000, X_scaled.shape[0])
                    if X_scaled.shape[0] > sample_size:
                        indices = np.random.choice(X_scaled.shape[0], sample_size, replace=False)
                        X_sample = X_scaled[indices]
                    else:
                        X_sample = X_scaled
                    
                    X_reduced = reducer.fit_transform(X_sample)
                    results['dimensionality_reduction'][name] = {
                        'data': X_reduced,
                        'n_components': X_reduced.shape[1],
                        'sample_indices': indices if X_scaled.shape[0] > sample_size else None
                    }
                else:
                    X_reduced = reducer.fit_transform(X_scaled)
                    results['dimensionality_reduction'][name] = {
                        'data': X_reduced,
                        'n_components': X_reduced.shape[1],
                        'explained_variance_ratio': (
                            reducer.explained_variance_ratio_ if hasattr(reducer, 'explained_variance_ratio_') else None
                        )
                    }
                
                logger.info(f"{name} reduced dimensions to {X_reduced.shape[1]}")
                
            except Exception as e:
                logger.error(f"Error in {name} reduction: {str(e)}")
                results['dimensionality_reduction'][name] = {'error': str(e)}
        
        return results
    
    def get_cluster_summaries(self, X: np.ndarray, cluster_labels: np.ndarray, feature_names: List[str] = None) -> Dict[int, Dict[str, Any]]:
        """Generate summaries for each cluster"""
        
        cluster_summaries = {}
        unique_clusters = set(cluster_labels) - {-1}  # Exclude noise points
        
        for cluster_id in unique_clusters:
            cluster_mask = cluster_labels == cluster_id
            cluster_data = X[cluster_mask]
            
            summary = {
                'size': np.sum(cluster_mask),
                'percentage': (np.sum(cluster_mask) / len(X)) * 100,
                'mean_values': np.mean(cluster_data, axis=0),
                'std_values': np.std(cluster_data, axis=0),
                'min_values': np.min(cluster_data, axis=0),
                'max_values': np.max(cluster_data, axis=0)
            }
            
            if feature_names:
                summary['feature_stats'] = {
                    feature_names[i]: {
                        'mean': summary['mean_values'][i],
                        'std': summary['std_values'][i],
                        'min': summary['min_values'][i],
                        'max': summary['max_values'][i]
                    }
                    for i in range(len(feature_names))
                }
            
            cluster_summaries[cluster_id] = summary
        
        return cluster_summaries


class HyperparameterOptimizer:
    """
    Automated hyperparameter optimization for ML models
    """
    
    def __init__(self):
        self.best_params = {}
        self.optimization_results = {}
    
    def optimize_regressor(self, 
                          model_type: str,
                          X_train: np.ndarray,
                          y_train: np.ndarray,
                          param_grid: Dict[str, List],
                          cv_folds: int = 5,
                          n_iter: int = 50,
                          search_type: str = 'random') -> Dict[str, Any]:
        """Optimize hyperparameters for regression models"""
        
        # Get base model
        base_models = {
            'random_forest': RandomForestRegressor(random_state=42, n_jobs=-1),
            'gradient_boosting': GradientBoostingRegressor(random_state=42),
            'svr': SVR(),
            'ridge': Ridge(random_state=42),
            'lasso': Lasso(random_state=42, max_iter=2000)
        }
        
        if model_type not in base_models:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        base_model = base_models[model_type]
        
        # Choose search strategy
        if search_type == 'grid':
            search = GridSearchCV(
                base_model, param_grid, cv=cv_folds,
                scoring='neg_mean_squared_error', n_jobs=-1, verbose=1
            )
        else:  # random search
            search = RandomizedSearchCV(
                base_model, param_grid, n_iter=n_iter, cv=cv_folds,
                scoring='neg_mean_squared_error', n_jobs=-1, verbose=1, random_state=42
            )
        
        logger.info(f"Optimizing {model_type} hyperparameters using {search_type} search...")
        
        # Perform search
        search.fit(X_train, y_train)
        
        results = {
            'best_params': search.best_params_,
            'best_score': -search.best_score_,  # Convert back to positive MSE
            'cv_results': search.cv_results_,
            'best_estimator': search.best_estimator_
        }
        
        self.best_params[model_type] = search.best_params_
        self.optimization_results[model_type] = results
        
        logger.info(f"Best {model_type} parameters: {search.best_params_}")
        logger.info(f"Best CV MSE: {-search.best_score_:.4f}")
        
        return results


def create_ml_pipeline(X_train: np.ndarray, 
                      y_train: np.ndarray,
                      X_test: np.ndarray,
                      y_test: np.ndarray,
                      task_type: str = 'regression',
                      optimize_hyperparams: bool = False) -> Dict[str, Any]:
    """
    Create comprehensive ML pipeline for database optimization tasks
    
    Args:
        X_train, y_train: Training data
        X_test, y_test: Test data  
        task_type: 'regression' or 'classification'
        optimize_hyperparams: Whether to perform hyperparameter optimization
        
    Returns:
        Dictionary with trained models and results
    """
    
    logger.info(f"Creating ML pipeline for {task_type} task")
    logger.info(f"Training data shape: {X_train.shape}, Test data shape: {X_test.shape}")
    
    results = {
        'task_type': task_type,
        'data_info': {
            'n_train_samples': X_train.shape[0],
            'n_test_samples': X_test.shape[0],
            'n_features': X_train.shape[1]
        },
        'models': {},
        'best_model': None,
        'feature_importance': {},
        'hyperparameter_optimization': {}
    }
    
    if task_type == 'regression':
        # Create regression suite
        regressor_suite = QueryPerformanceRegressor()
        
        # Hyperparameter optimization if requested
        if optimize_hyperparams:
            optimizer = HyperparameterOptimizer()
            
            # Define parameter grids
            param_grids = {
                'random_forest': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4]
                },
                'gradient_boosting': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'min_samples_split': [2, 5, 10]
                }
            }
            
            for model_name, param_grid in param_grids.items():
                opt_results = optimizer.optimize_regressor(
                    model_name, X_train, y_train, param_grid, search_type='random', n_iter=20
                )
                results['hyperparameter_optimization'][model_name] = opt_results
        
        # Train and evaluate models
        model_results = regressor_suite.train_and_evaluate(X_train, y_train, X_test, y_test)
        results['models'] = model_results
        results['best_model'] = regressor_suite.best_model_name
        
        # Create ensemble
        ensemble = regressor_suite.create_ensemble()
        results['ensemble'] = ensemble
        
        # Get feature importance
        results['feature_importance'] = regressor_suite.get_feature_importance()
        
    elif task_type == 'classification':
        # Create classification suite
        classifier_suite = QueryClassificationSuite()
        
        # Train and evaluate models
        model_results = classifier_suite.train_and_evaluate(X_train, y_train, X_test, y_test)
        results['models'] = model_results
        results['best_model'] = classifier_suite.best_model_name
        
    else:
        raise ValueError(f"Unsupported task type: {task_type}")
    
    logger.info(f"ML pipeline completed. Best model: {results['best_model']}")
    
    return results


if __name__ == "__main__":
    # Example usage and testing
    logger.info("Testing Scikit-learn models for AgenticAI4DB")
    
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    X = np.random.randn(n_samples, n_features)
    
    # Create correlated features for more realistic data
    X[:, 1] = X[:, 0] + np.random.normal(0, 0.5, n_samples)
    X[:, 2] = np.abs(X[:, 0]) + np.random.normal(0, 0.3, n_samples)
    
    # Regression target (execution time)
    y_regression = (
        2 * X[:, 0] + 1.5 * X[:, 1] + 0.8 * X[:, 2] + 
        np.random.normal(0, 0.5, n_samples)
    )
    y_regression = np.maximum(0, y_regression)  # Ensure positive
    
    # Classification target (query type)
    query_type_probs = 1 / (1 + np.exp(-(X[:, 0] + X[:, 1])))
    y_classification = np.random.binomial(3, query_type_probs, n_samples)  # 4 classes
    
    # Split data
    X_train, X_test, y_reg_train, y_reg_test = train_test_split(
        X, y_regression, test_size=0.2, random_state=42
    )
    _, _, y_class_train, y_class_test = train_test_split(
        X, y_classification, test_size=0.2, random_state=42
    )
    
    # Test regression pipeline
    logger.info("Testing regression pipeline")
    regression_results = create_ml_pipeline(
        X_train, y_reg_train, X_test, y_reg_test, 
        task_type='regression', optimize_hyperparams=False
    )
    
    print(f"\nRegression Results:")
    print(f"Best model: {regression_results['best_model']}")
    if regression_results['best_model']:
        best_metrics = regression_results['models'][regression_results['best_model']]
        print(f"Test R²: {best_metrics['test_r2']:.4f}")
        print(f"Test MSE: {best_metrics['test_mse']:.4f}")
    
    # Test classification pipeline
    logger.info("Testing classification pipeline")
    classification_results = create_ml_pipeline(
        X_train, y_class_train, X_test, y_class_test,
        task_type='classification', optimize_hyperparams=False
    )
    
    print(f"\nClassification Results:")
    print(f"Best model: {classification_results['best_model']}")
    if classification_results['best_model']:
        best_metrics = classification_results['models'][classification_results['best_model']]
        print(f"Test Accuracy: {best_metrics['test_accuracy']:.4f}")
        print(f"Test F1: {best_metrics['test_f1']:.4f}")
    
    # Test clustering
    logger.info("Testing clustering analysis")
    cluster_analyzer = DatabaseClusterAnalyzer()
    cluster_results = cluster_analyzer.analyze_clusters(X, n_clusters_range=(2, 8))
    
    print(f"\nClustering Results:")
    for method, metrics in cluster_results['cluster_metrics'].items():
        print(f"{method}: {metrics['n_clusters']} clusters, "
              f"Silhouette score: {metrics['silhouette_score']:.4f}")
    
    logger.info("All Scikit-learn models tested successfully!")