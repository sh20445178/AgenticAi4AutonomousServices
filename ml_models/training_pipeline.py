"""
Comprehensive ML Training Pipeline for AgenticAI4DB
Orchestrates TensorFlow and Scikit-learn models for database optimization
"""

import os
import sys
import json
import logging
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import joblib
from pathlib import Path

# Import custom modules
try:
    from .data_preprocessing import DatabasePreprocessor, QueryPatternAnalyzer
    from .tensorflow_models import (
        QueryPerformancePredictor, QueryAnomalyDetector, 
        QueryClassifier, DatabaseOptimizationRecommender
    )
    from .sklearn_models import (
        QueryPerformanceRegressor, QueryClassificationSuite,
        DatabaseClusterAnalyzer, HyperparameterOptimizer,
        create_ml_pipeline
    )
except ImportError:
    # For standalone execution
    sys.path.append(os.path.dirname(__file__))
    from data_preprocessing import DatabasePreprocessor, QueryPatternAnalyzer
    from tensorflow_models import (
        QueryPerformancePredictor, QueryAnomalyDetector,
        QueryClassifier, DatabaseOptimizationRecommender
    )
    from sklearn_models import (
        QueryPerformanceRegressor, QueryClassificationSuite,
        DatabaseClusterAnalyzer, HyperparameterOptimizer,
        create_ml_pipeline
    )

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLTrainingPipeline:
    """
    Comprehensive ML training pipeline for database optimization
    """
    
    def __init__(self, 
                 output_dir: str = "trained_models",
                 use_synthetic_data: bool = True,
                 data_size: int = 5000):
        """
        Initialize training pipeline
        
        Args:
            output_dir: Directory to save trained models
            use_synthetic_data: Whether to generate synthetic data for training
            data_size: Size of synthetic dataset
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.use_synthetic_data = use_synthetic_data
        self.data_size = data_size
        
        # Initialize components
        self.preprocessor = DatabasePreprocessor()
        self.pattern_analyzer = QueryPatternAnalyzer()
        
        # Model containers
        self.tensorflow_models = {}
        self.sklearn_models = {}
        self.model_metadata = {}
        
        # Training data
        self.training_data = {}
        self.model_performance = {}
        
        logger.info(f"Initialized ML Training Pipeline with output directory: {self.output_dir}")
    
    def prepare_training_data(self, 
                            queries: Optional[List[str]] = None,
                            performance_metrics: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Prepare training data from queries and performance metrics
        """
        logger.info("Preparing training data...")
        
        if self.use_synthetic_data or queries is None:
            logger.info(f"Generating {self.data_size} synthetic training samples")
            queries, performance_metrics = self.preprocessor.generate_synthetic_data(self.data_size)
        
        # Extract query patterns
        query_patterns = self.pattern_analyzer.extract_query_patterns(queries)
        
        # Create feature matrices
        query_features = self.preprocessor.preprocess_query_features(queries)
        performance_features, feature_names = self.preprocessor.preprocess_performance_metrics(
            performance_metrics.drop(['execution_time_ms', 'query_type'], axis=1, errors='ignore')
        )
        
        # Combine features
        if query_features.shape[0] != performance_features.shape[0]:
            min_samples = min(query_features.shape[0], performance_features.shape[0])
            query_features = query_features[:min_samples]
            performance_features = performance_features[:min_samples]
            performance_metrics = performance_metrics.iloc[:min_samples]
            queries = queries[:min_samples]
        
        X_features = np.hstack([query_features, performance_features])
        
        # Prepare different target variables
        targets = {
            'execution_time': performance_metrics['execution_time_ms'].values,
            'query_types': performance_metrics['query_type'].values,
            'complexity_scores': np.array([pattern['complexity_score'] for pattern in query_patterns]),
            'optimization_flags': self._generate_optimization_flags(performance_metrics)
        }
        
        # Create TF-IDF vectors for similarity analysis
        tfidf_features = self.preprocessor.vectorize_queries_for_similarity(queries)
        
        self.training_data = {
            'features': X_features,
            'tfidf_features': tfidf_features,
            'targets': targets,
            'queries': queries,
            'performance_metrics': performance_metrics,
            'query_patterns': query_patterns,
            'feature_names': [f'query_feat_{i}' for i in range(query_features.shape[1])] + feature_names
        }
        
        logger.info(f"Prepared training data: {X_features.shape[0]} samples, {X_features.shape[1]} features")
        return self.training_data
    
    def _generate_optimization_flags(self, performance_df: pd.DataFrame) -> np.ndarray:
        """Generate multi-label optimization recommendations"""
        flags = np.zeros((len(performance_df), 5))  # 5 optimization categories
        
        # Index needed (high execution time + low cache hit ratio)
        flags[:, 0] = (
            (performance_df['execution_time_ms'] > performance_df['execution_time_ms'].quantile(0.75)) &
            (performance_df['cache_hit_ratio'] < 0.7)
        ).astype(int)
        
        # Query rewrite needed (high complexity + many rows examined)
        flags[:, 1] = (
            (performance_df['query_complexity_score'] > 7) &
            (performance_df['rows_examined'] > performance_df['rows_returned'] * 10)
        ).astype(int)
        
        # Schema change needed (many tables + high disk I/O)
        flags[:, 2] = (
            (performance_df['table_count'] > 5) &
            (performance_df['disk_io_operations'] > performance_df['disk_io_operations'].quantile(0.8))
        ).astype(int)
        
        # Partitioning needed (large tables + range queries)
        flags[:, 3] = (
            (performance_df['rows_examined'] > 100000) &
            (performance_df['query_complexity_score'] > 5)
        ).astype(int)
        
        # Caching needed (frequent similar queries)
        flags[:, 4] = (
            performance_df['cache_hit_ratio'] < 0.5
        ).astype(int)
        
        return flags
    
    def train_tensorflow_models(self, validation_split: float = 0.2) -> Dict[str, Any]:
        """Train all TensorFlow models"""
        logger.info("Training TensorFlow models...")
        
        if not self.training_data:
            raise ValueError("Training data not prepared. Call prepare_training_data() first.")
        
        X = self.training_data['features']
        targets = self.training_data['targets']
        
        # Split data for validation
        from sklearn.model_selection import train_test_split
        
        results = {}
        
        # 1. Query Performance Predictor
        logger.info("Training TensorFlow Query Performance Predictor...")
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, targets['execution_time'], test_size=validation_split, random_state=42
        )
        
        perf_predictor = QueryPerformancePredictor(input_dim=X.shape[1])
        perf_predictor.build_model()
        
        history = perf_predictor.train(X_train, y_train, X_val, y_val, epochs=50, patience=10)
        
        # Evaluate
        metrics = perf_predictor.evaluate(X_val, y_val)
        results['performance_predictor'] = {
            'model': perf_predictor,
            'metrics': metrics,
            'history': history.history if history else None
        }
        
        self.tensorflow_models['performance_predictor'] = perf_predictor
        logger.info(f"Performance Predictor - R²: {metrics['r2_score']:.4f}, MAE: {metrics['test_mae']:.4f}")
        
        # 2. Query Anomaly Detector
        logger.info("Training TensorFlow Query Anomaly Detector...")
        
        anomaly_detector = QueryAnomalyDetector(input_dim=X.shape[1])
        anomaly_detector.build_model()
        
        # Train on normal patterns (use majority of data as "normal")
        normal_indices = np.random.choice(len(X), int(len(X) * 0.8), replace=False)
        X_normal = X[normal_indices]
        
        X_norm_train, X_norm_val = train_test_split(X_normal, test_size=0.2, random_state=42)
        
        anomaly_history = anomaly_detector.train(X_norm_train, X_norm_val, epochs=50, patience=10)
        
        # Test anomaly detection
        anomalies, scores = anomaly_detector.detect_anomalies(X_val)
        anomaly_rate = np.mean(anomalies)
        
        results['anomaly_detector'] = {
            'model': anomaly_detector,
            'anomaly_rate': anomaly_rate,
            'threshold': anomaly_detector.threshold,
            'history': anomaly_history.history if anomaly_history else None
        }
        
        self.tensorflow_models['anomaly_detector'] = anomaly_detector
        logger.info(f"Anomaly Detector - Threshold: {anomaly_detector.threshold:.4f}, "
                   f"Anomaly rate: {anomaly_rate:.2%}")
        
        # 3. Query Classifier
        logger.info("Training TensorFlow Query Classifier...")
        
        # Encode query types to integers
        from sklearn.preprocessing import LabelEncoder
        label_encoder = LabelEncoder()
        y_types_encoded = label_encoder.fit_transform(targets['query_types'])
        n_classes = len(label_encoder.classes_)
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y_types_encoded, test_size=validation_split, random_state=42, stratify=y_types_encoded
        )
        
        query_classifier = QueryClassifier(input_dim=X.shape[1], num_classes=n_classes)
        query_classifier.build_model()
        
        classifier_history = query_classifier.train(X_train, y_train, X_val, y_val, epochs=30)
        
        # Evaluate
        predictions = query_classifier.predict(X_val)
        accuracy = np.mean(predictions == y_val)
        
        results['query_classifier'] = {
            'model': query_classifier,
            'accuracy': accuracy,
            'label_encoder': label_encoder,
            'history': classifier_history.history if classifier_history else None
        }
        
        self.tensorflow_models['query_classifier'] = query_classifier
        logger.info(f"Query Classifier - Accuracy: {accuracy:.4f}")
        
        # 4. Database Optimization Recommender
        logger.info("Training TensorFlow Optimization Recommender...")
        
        X_train, X_val, y_perf_train, y_perf_val = train_test_split(
            X, targets['execution_time'], test_size=validation_split, random_state=42
        )
        _, _, y_comp_train, y_comp_val = train_test_split(
            X, (targets['complexity_scores'] > np.median(targets['complexity_scores'])).astype(float),
            test_size=validation_split, random_state=42
        )
        _, _, y_opt_train, y_opt_val = train_test_split(
            X, targets['optimization_flags'], test_size=validation_split, random_state=42
        )
        
        optimizer = DatabaseOptimizationRecommender(feature_dim=X.shape[1])
        optimizer.build_ensemble()
        
        validation_data = (X_val, {
            'performance_score': y_perf_val,
            'complexity_score': y_comp_val,
            'recommendations': y_opt_val
        })
        
        opt_history = optimizer.train_ensemble(
            X_train, y_perf_train, y_comp_train, y_opt_train,
            validation_data=validation_data, epochs=30
        )
        
        # Test recommendations
        recommendations = optimizer.get_recommendations(X_val)
        
        results['optimization_recommender'] = {
            'model': optimizer,
            'sample_recommendations': recommendations,
            'history': opt_history.history if opt_history else None
        }
        
        self.tensorflow_models['optimization_recommender'] = optimizer
        logger.info("Optimization Recommender trained successfully")
        
        self.model_performance['tensorflow'] = results
        return results
    
    def train_sklearn_models(self, validation_split: float = 0.2) -> Dict[str, Any]:
        """Train all Scikit-learn models"""
        logger.info("Training Scikit-learn models...")
        
        if not self.training_data:
            raise ValueError("Training data not prepared. Call prepare_training_data() first.")
        
        X = self.training_data['features']
        targets = self.training_data['targets']
        
        from sklearn.model_selection import train_test_split
        
        results = {}
        
        # 1. Regression Models
        logger.info("Training Scikit-learn regression models...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, targets['execution_time'], test_size=validation_split, random_state=42
        )
        
        regression_results = create_ml_pipeline(
            X_train, y_train, X_test, y_test,
            task_type='regression', optimize_hyperparams=False
        )
        
        results['regression'] = regression_results
        self.sklearn_models['regression'] = regression_results
        
        # 2. Classification Models
        logger.info("Training Scikit-learn classification models...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, targets['query_types'], test_size=validation_split, random_state=42, 
            stratify=targets['query_types']
        )
        
        classification_results = create_ml_pipeline(
            X_train, y_train, X_test, y_test,
            task_type='classification', optimize_hyperparams=False
        )
        
        results['classification'] = classification_results
        self.sklearn_models['classification'] = classification_results
        
        # 3. Clustering Analysis
        logger.info("Performing clustering analysis...")
        
        cluster_analyzer = DatabaseClusterAnalyzer()
        cluster_results = cluster_analyzer.analyze_clusters(X, n_clusters_range=(3, 10))
        
        results['clustering'] = cluster_results
        self.sklearn_models['clustering'] = cluster_analyzer
        
        logger.info("Scikit-learn models training completed")
        
        self.model_performance['sklearn'] = results
        return results
    
    def evaluate_all_models(self) -> Dict[str, Any]:
        """Comprehensive evaluation of all trained models"""
        logger.info("Evaluating all trained models...")
        
        evaluation_results = {
            'timestamp': datetime.now().isoformat(),
            'tensorflow_models': {},
            'sklearn_models': {},
            'model_comparison': {},
            'recommendations': []
        }
        
        # TensorFlow model evaluation
        if 'tensorflow' in self.model_performance:
            tf_results = self.model_performance['tensorflow']
            
            evaluation_results['tensorflow_models'] = {
                'performance_predictor': {
                    'r2_score': tf_results['performance_predictor']['metrics']['r2_score'],
                    'mae': tf_results['performance_predictor']['metrics']['test_mae'],
                    'mse': tf_results['performance_predictor']['metrics']['test_loss']
                },
                'anomaly_detector': {
                    'threshold': tf_results['anomaly_detector']['threshold'],
                    'anomaly_rate': tf_results['anomaly_detector']['anomaly_rate']
                },
                'query_classifier': {
                    'accuracy': tf_results['query_classifier']['accuracy']
                }
            }
        
        # Scikit-learn model evaluation
        if 'sklearn' in self.model_performance:
            sklearn_results = self.model_performance['sklearn']
            
            # Regression evaluation
            if 'regression' in sklearn_results and sklearn_results['regression']['best_model']:
                best_reg_model = sklearn_results['regression']['best_model']
                reg_metrics = sklearn_results['regression']['models'][best_reg_model]
                
                evaluation_results['sklearn_models']['regression'] = {
                    'best_model': best_reg_model,
                    'r2_score': reg_metrics['test_r2'],
                    'mae': reg_metrics['test_mae'],
                    'mse': reg_metrics['test_mse']
                }
            
            # Classification evaluation
            if 'classification' in sklearn_results and sklearn_results['classification']['best_model']:
                best_class_model = sklearn_results['classification']['best_model']
                class_metrics = sklearn_results['classification']['models'][best_class_model]
                
                evaluation_results['sklearn_models']['classification'] = {
                    'best_model': best_class_model,
                    'accuracy': class_metrics['test_accuracy'],
                    'f1_score': class_metrics['test_f1'],
                    'precision': class_metrics['test_precision'],
                    'recall': class_metrics['test_recall']
                }
            
            # Clustering evaluation
            if 'clustering' in sklearn_results:
                cluster_metrics = sklearn_results['clustering']['cluster_metrics']
                best_clustering = max(cluster_metrics.items(), 
                                    key=lambda x: x[1]['silhouette_score'])
                
                evaluation_results['sklearn_models']['clustering'] = {
                    'best_method': best_clustering[0],
                    'n_clusters': best_clustering[1]['n_clusters'],
                    'silhouette_score': best_clustering[1]['silhouette_score']
                }
        
        # Model comparison and recommendations
        evaluation_results['recommendations'] = self._generate_model_recommendations(evaluation_results)
        
        # Save evaluation results
        eval_file = self.output_dir / 'model_evaluation.json'
        with open(eval_file, 'w') as f:
            json.dump(evaluation_results, f, indent=2, default=str)
        
        logger.info(f"Model evaluation completed. Results saved to {eval_file}")
        return evaluation_results
    
    def _generate_model_recommendations(self, evaluation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on model performance"""
        recommendations = []
        
        # Performance prediction recommendations
        tf_perf = evaluation_results.get('tensorflow_models', {}).get('performance_predictor', {})
        sklearn_perf = evaluation_results.get('sklearn_models', {}).get('regression', {})
        
        if tf_perf.get('r2_score', 0) > 0.8:
            recommendations.append("TensorFlow performance predictor shows excellent accuracy (R² > 0.8) - suitable for production")
        elif sklearn_perf.get('r2_score', 0) > tf_perf.get('r2_score', 0):
            recommendations.append(f"Scikit-learn {sklearn_perf.get('best_model', 'regression')} outperforms TensorFlow for performance prediction")
        
        # Classification recommendations
        tf_class = evaluation_results.get('tensorflow_models', {}).get('query_classifier', {})
        sklearn_class = evaluation_results.get('sklearn_models', {}).get('classification', {})
        
        if tf_class.get('accuracy', 0) > 0.9:
            recommendations.append("Query classification model achieves high accuracy (>90%) - ready for deployment")
        elif sklearn_class.get('accuracy', 0) > tf_class.get('accuracy', 0):
            recommendations.append(f"Scikit-learn {sklearn_class.get('best_model', 'classifier')} recommended for query classification")
        
        # Anomaly detection recommendations
        anomaly_rate = evaluation_results.get('tensorflow_models', {}).get('anomaly_detector', {}).get('anomaly_rate', 0)
        if 0.01 < anomaly_rate < 0.1:
            recommendations.append("Anomaly detection model shows reasonable anomaly rate (1-10%) - suitable for monitoring")
        elif anomaly_rate > 0.2:
            recommendations.append("High anomaly rate detected - consider adjusting threshold or reviewing training data")
        
        # Clustering recommendations
        clustering = evaluation_results.get('sklearn_models', {}).get('clustering', {})
        if clustering.get('silhouette_score', 0) > 0.5:
            recommendations.append(f"Good clustering structure found with {clustering.get('best_method')} - useful for query pattern analysis")
        
        return recommendations
    
    def save_all_models(self) -> Dict[str, str]:
        """Save all trained models to disk"""
        logger.info("Saving all trained models...")
        
        saved_models = {}
        
        # Save TensorFlow models
        for name, model in self.tensorflow_models.items():
            model_path = self.output_dir / f"tensorflow_{name}.keras"
            
            try:
                if hasattr(model, 'save_model'):
                    model.save_model(str(model_path))
                else:
                    model.model.save(str(model_path))
                
                saved_models[f"tensorflow_{name}"] = str(model_path)
                logger.info(f"Saved TensorFlow {name} to {model_path}")
            except Exception as e:
                logger.error(f"Error saving TensorFlow {name}: {str(e)}")
        
        # Save Scikit-learn models
        for category, models in self.sklearn_models.items():
            model_path = self.output_dir / f"sklearn_{category}.joblib"
            
            try:
                joblib.dump(models, model_path)
                saved_models[f"sklearn_{category}"] = str(model_path)
                logger.info(f"Saved Scikit-learn {category} to {model_path}")
            except Exception as e:
                logger.error(f"Error saving Scikit-learn {category}: {str(e)}")
        
        # Save preprocessor
        preprocessor_path = self.output_dir / "preprocessor.joblib"
        try:
            self.preprocessor.save_preprocessor(str(preprocessor_path))
            saved_models["preprocessor"] = str(preprocessor_path)
        except Exception as e:
            logger.error(f"Error saving preprocessor: {str(e)}")
        
        # Save model metadata
        metadata = {
            'training_timestamp': datetime.now().isoformat(),
            'data_size': self.data_size,
            'feature_count': self.training_data.get('features', np.array([])).shape[1] if self.training_data else 0,
            'model_files': saved_models,
            'performance_summary': self.model_performance
        }
        
        metadata_path = self.output_dir / "model_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        saved_models["metadata"] = str(metadata_path)
        
        logger.info(f"All models saved successfully. Metadata: {metadata_path}")
        return saved_models
    
    def run_full_pipeline(self, 
                         queries: Optional[List[str]] = None,
                         performance_metrics: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Run the complete ML training pipeline"""
        logger.info("Starting full ML training pipeline...")
        
        pipeline_start = datetime.now()
        
        try:
            # Step 1: Prepare data
            self.prepare_training_data(queries, performance_metrics)
            
            # Step 2: Train TensorFlow models
            tf_results = self.train_tensorflow_models()
            
            # Step 3: Train Scikit-learn models
            sklearn_results = self.train_sklearn_models()
            
            # Step 4: Evaluate all models
            evaluation_results = self.evaluate_all_models()
            
            # Step 5: Save models
            saved_models = self.save_all_models()
            
            pipeline_duration = datetime.now() - pipeline_start
            
            summary = {
                'status': 'completed',
                'duration': str(pipeline_duration),
                'models_trained': {
                    'tensorflow': len(self.tensorflow_models),
                    'sklearn': len(self.sklearn_models)
                },
                'evaluation_results': evaluation_results,
                'saved_models': saved_models,
                'recommendations': evaluation_results.get('recommendations', [])
            }
            
            logger.info(f"Pipeline completed successfully in {pipeline_duration}")
            logger.info(f"Trained {len(self.tensorflow_models)} TensorFlow and {len(self.sklearn_models)} Scikit-learn model suites")
            
            return summary
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'duration': str(datetime.now() - pipeline_start)
            }


def main():
    """Main function to run the training pipeline"""
    logger.info("AgenticAI4DB ML Training Pipeline")
    logger.info("=" * 50)
    
    # Initialize pipeline
    pipeline = MLTrainingPipeline(
        output_dir="trained_models",
        use_synthetic_data=True,
        data_size=2000
    )
    
    # Run full pipeline
    results = pipeline.run_full_pipeline()
    
    # Print summary
    print(f"\nPipeline Status: {results['status']}")
    print(f"Duration: {results.get('duration', 'N/A')}")
    
    if results['status'] == 'completed':
        print(f"\nModels Trained:")
        print(f"  - TensorFlow models: {results['models_trained']['tensorflow']}")
        print(f"  - Scikit-learn models: {results['models_trained']['sklearn']}")
        
        print(f"\nModel Files Saved:")
        for model_name, file_path in results['saved_models'].items():
            print(f"  - {model_name}: {file_path}")
        
        print(f"\nRecommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    else:
        print(f"Error: {results.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()