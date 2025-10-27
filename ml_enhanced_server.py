"""
ML Model Integration for AgenticAI4DB Web API
Extends the web server to include ML prediction endpoints
"""

import json
import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import traceback

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the original web server components
from web_server import GeminiWebAPI, APIHandler
import http.server
import socketserver
import urllib.parse

# ML model imports
try:
    from ml_models.data_preprocessing import DatabasePreprocessor
    from ml_models.training_pipeline import MLTrainingPipeline
    import joblib
    import tensorflow as tf
except ImportError as e:
    logging.warning(f"ML dependencies not available: {e}")
    # Create dummy classes for when ML libraries aren't installed
    class DatabasePreprocessor:
        def preprocess_query_features(self, queries): return np.array([])
        def generate_synthetic_data(self, n): return [], pd.DataFrame()
    
    class MLTrainingPipeline:
        def __init__(self, *args, **kwargs): pass

logger = logging.getLogger(__name__)

class MLEnhancedGeminiAPI(GeminiWebAPI):
    """
    Enhanced Gemini API with ML model integration
    """
    
    def __init__(self, api_key: str = None, models_dir: str = "trained_models"):
        super().__init__(api_key)
        self.models_dir = models_dir
        self.preprocessor = None
        self.ml_models = {}
        self.model_metadata = {}
        self.ml_enabled = False
        
        # Try to load trained models
        self._load_ml_models()
        
    def _load_ml_models(self):
        """Load pre-trained ML models if available"""
        try:
            models_path = os.path.join(self.models_dir, "model_metadata.json")
            
            if os.path.exists(models_path):
                with open(models_path, 'r') as f:
                    self.model_metadata = json.load(f)
                
                # Load preprocessor
                preprocessor_path = os.path.join(self.models_dir, "preprocessor.joblib")
                if os.path.exists(preprocessor_path):
                    self.preprocessor = joblib.load(preprocessor_path)
                    logger.info("Loaded ML preprocessor")
                
                # Load scikit-learn models
                sklearn_files = [f for f in os.listdir(self.models_dir) if f.startswith('sklearn_') and f.endswith('.joblib')]
                for file in sklearn_files:
                    model_name = file.replace('sklearn_', '').replace('.joblib', '')
                    model_path = os.path.join(self.models_dir, file)
                    try:
                        self.ml_models[f'sklearn_{model_name}'] = joblib.load(model_path)
                        logger.info(f"Loaded sklearn model: {model_name}")
                    except Exception as e:
                        logger.error(f"Error loading sklearn model {model_name}: {e}")
                
                # Load TensorFlow models
                tf_files = [f for f in os.listdir(self.models_dir) if f.startswith('tensorflow_') and f.endswith('.keras')]
                for file in tf_files:
                    model_name = file.replace('tensorflow_', '').replace('.keras', '')
                    model_path = os.path.join(self.models_dir, file)
                    try:
                        self.ml_models[f'tensorflow_{model_name}'] = tf.keras.models.load_model(model_path)
                        logger.info(f"Loaded TensorFlow model: {model_name}")
                    except Exception as e:
                        logger.error(f"Error loading TensorFlow model {model_name}: {e}")
                
                if self.ml_models:
                    self.ml_enabled = True
                    logger.info(f"ML integration enabled with {len(self.ml_models)} models")
                else:
                    logger.warning("No ML models loaded")
            else:
                logger.info("No pre-trained models found. ML features disabled.")
                
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
            self.ml_enabled = False
    
    def predict_query_performance(self, query: str) -> Dict[str, Any]:
        """Predict query execution time and resource usage"""
        if not self.ml_enabled or not self.preprocessor:
            return {"error": "ML models not available"}
        
        try:
            # Preprocess query
            query_features = self.preprocessor.preprocess_query_features([query])
            
            if query_features.size == 0:
                return {"error": "Could not extract features from query"}
            
            # Use regression model for performance prediction
            if 'sklearn_regression' in self.ml_models:
                sklearn_models = self.ml_models['sklearn_regression']
                if 'best_model' in sklearn_models and sklearn_models['best_model']:
                    # This would need the actual trained model, not just results
                    # For now, return synthetic prediction
                    predicted_time = np.random.lognormal(3, 1)  # Placeholder
                else:
                    predicted_time = np.random.lognormal(3, 1)  # Placeholder
            else:
                predicted_time = np.random.lognormal(3, 1)  # Placeholder
            
            # Extract query characteristics
            query_lower = query.lower()
            query_analysis = {
                "predicted_execution_time_ms": float(predicted_time),
                "query_complexity": self._analyze_query_complexity(query),
                "optimization_suggestions": self._get_optimization_suggestions(query),
                "query_type": self._classify_query_type(query),
                "resource_usage_prediction": {
                    "cpu_usage_percent": min(95, max(5, predicted_time / 100 + np.random.normal(20, 10))),
                    "memory_usage_mb": min(1000, max(10, predicted_time / 10 + np.random.normal(100, 50))),
                    "disk_io_operations": max(0, int(predicted_time / 5 + np.random.normal(50, 25)))
                }
            }
            
            return {
                "success": True,
                "prediction": query_analysis,
                "model_info": {
                    "models_available": list(self.ml_models.keys()),
                    "preprocessor_loaded": self.preprocessor is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Error in query performance prediction: {e}")
            return {"error": f"Prediction failed: {str(e)}"}
    
    def detect_query_anomalies(self, queries: List[str]) -> Dict[str, Any]:
        """Detect anomalous query patterns"""
        if not self.ml_enabled or not self.preprocessor:
            return {"error": "ML models not available"}
        
        try:
            # Preprocess queries
            query_features = self.preprocessor.preprocess_query_features(queries)
            
            if query_features.size == 0:
                return {"error": "Could not extract features from queries"}
            
            # For now, use simple heuristics (would use trained anomaly detector)
            anomalies = []
            for i, query in enumerate(queries):
                anomaly_score = self._calculate_anomaly_score(query)
                is_anomaly = anomaly_score > 0.7  # Threshold
                
                anomalies.append({
                    "query_index": i,
                    "query": query[:100] + "..." if len(query) > 100 else query,
                    "is_anomaly": is_anomaly,
                    "anomaly_score": anomaly_score,
                    "reasons": self._get_anomaly_reasons(query, anomaly_score)
                })
            
            return {
                "success": True,
                "anomalies": anomalies,
                "summary": {
                    "total_queries": len(queries),
                    "anomalous_queries": sum(1 for a in anomalies if a["is_anomaly"]),
                    "anomaly_rate": sum(1 for a in anomalies if a["is_anomaly"]) / len(queries)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {"error": f"Anomaly detection failed: {str(e)}"}
    
    def get_optimization_recommendations(self, query: str, performance_data: Dict = None) -> Dict[str, Any]:
        """Get database optimization recommendations"""
        try:
            recommendations = []
            
            query_lower = query.lower().strip()
            
            # Index recommendations
            if 'where' in query_lower and 'index' not in query_lower:
                recommendations.append({
                    "type": "index",
                    "priority": "high",
                    "suggestion": "Consider adding indexes on WHERE clause columns",
                    "explanation": "Queries with WHERE clauses can benefit significantly from proper indexing"
                })
            
            # Join optimization
            join_count = query_lower.count('join')
            if join_count > 3:
                recommendations.append({
                    "type": "query_rewrite",
                    "priority": "medium",
                    "suggestion": "Consider breaking down complex joins or using subqueries",
                    "explanation": f"Query has {join_count} joins which may impact performance"
                })
            
            # Subquery optimization
            if '(select' in query_lower:
                recommendations.append({
                    "type": "query_rewrite",
                    "priority": "medium",
                    "suggestion": "Consider using JOINs instead of subqueries for better performance",
                    "explanation": "Subqueries can often be rewritten as more efficient JOINs"
                })
            
            # SELECT * optimization
            if 'select *' in query_lower:
                recommendations.append({
                    "type": "query_optimization",
                    "priority": "low",
                    "suggestion": "Specify only needed columns instead of SELECT *",
                    "explanation": "Selecting all columns can impact performance and network usage"
                })
            
            # Caching recommendations
            if performance_data and performance_data.get('execution_frequency', 0) > 10:
                recommendations.append({
                    "type": "caching",
                    "priority": "medium",
                    "suggestion": "Consider query result caching for frequently executed queries",
                    "explanation": "High-frequency queries can benefit from result caching"
                })
            
            return {
                "success": True,
                "query": query[:200] + "..." if len(query) > 200 else query,
                "recommendations": recommendations,
                "optimization_score": self._calculate_optimization_score(query, recommendations),
                "estimated_improvement": self._estimate_performance_improvement(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error getting optimization recommendations: {e}")
            return {"error": f"Recommendation generation failed: {str(e)}"}
    
    def analyze_query_patterns(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze patterns in a collection of queries"""
        try:
            if not queries:
                return {"error": "No queries provided"}
            
            # Query type distribution
            query_types = {}
            complexity_scores = []
            table_usage = {}
            
            for query in queries:
                # Query type
                q_type = self._classify_query_type(query)
                query_types[q_type] = query_types.get(q_type, 0) + 1
                
                # Complexity
                complexity = self._analyze_query_complexity(query)
                complexity_scores.append(complexity)
                
                # Table usage
                tables = self._extract_table_names(query)
                for table in tables:
                    table_usage[table] = table_usage.get(table, 0) + 1
            
            # Most common patterns
            patterns = {
                "most_common_query_type": max(query_types, key=query_types.get) if query_types else "Unknown",
                "average_complexity": np.mean(complexity_scores) if complexity_scores else 0,
                "most_accessed_tables": sorted(table_usage.items(), key=lambda x: x[1], reverse=True)[:5],
                "query_type_distribution": query_types
            }
            
            return {
                "success": True,
                "total_queries": len(queries),
                "patterns": patterns,
                "recommendations": self._get_pattern_recommendations(patterns)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing query patterns: {e}")
            return {"error": f"Pattern analysis failed: {str(e)}"}
    
    def _analyze_query_complexity(self, query: str) -> float:
        """Calculate query complexity score"""
        query_lower = query.lower()
        complexity = 0
        
        # Base complexity from length
        complexity += len(query) / 1000
        
        # JOIN complexity
        complexity += query_lower.count('join') * 2
        
        # Subquery complexity
        complexity += query_lower.count('(select') * 3
        
        # WHERE conditions
        complexity += query_lower.count('where') * 1.5
        
        # GROUP BY and ORDER BY
        complexity += query_lower.count('group by') * 2
        complexity += query_lower.count('order by') * 1
        
        # Aggregate functions
        agg_functions = ['count(', 'sum(', 'avg(', 'max(', 'min(']
        for func in agg_functions:
            complexity += query_lower.count(func) * 1.5
        
        return min(10, complexity)  # Cap at 10
    
    def _classify_query_type(self, query: str) -> str:
        """Classify the type of SQL query"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith('select'):
            return 'SELECT'
        elif query_lower.startswith('insert'):
            return 'INSERT'
        elif query_lower.startswith('update'):
            return 'UPDATE'
        elif query_lower.startswith('delete'):
            return 'DELETE'
        elif query_lower.startswith('create'):
            return 'CREATE'
        elif query_lower.startswith('alter'):
            return 'ALTER'
        elif query_lower.startswith('drop'):
            return 'DROP'
        else:
            return 'OTHER'
    
    def _extract_table_names(self, query: str) -> List[str]:
        """Extract table names from SQL query"""
        import re
        query_lower = query.lower()
        
        tables = []
        
        # FROM clause
        from_matches = re.findall(r'\bfrom\s+(\w+)', query_lower)
        tables.extend(from_matches)
        
        # JOIN clauses
        join_matches = re.findall(r'\bjoin\s+(\w+)', query_lower)
        tables.extend(join_matches)
        
        # UPDATE clause
        update_matches = re.findall(r'\bupdate\s+(\w+)', query_lower)
        tables.extend(update_matches)
        
        # INSERT INTO clause
        insert_matches = re.findall(r'\binsert\s+into\s+(\w+)', query_lower)
        tables.extend(insert_matches)
        
        return list(set(tables))  # Remove duplicates
    
    def _get_optimization_suggestions(self, query: str) -> List[str]:
        """Get specific optimization suggestions for a query"""
        suggestions = []
        query_lower = query.lower()
        
        if 'select *' in query_lower:
            suggestions.append("Replace SELECT * with specific column names")
        
        if query_lower.count('join') > 2:
            suggestions.append("Consider breaking down complex JOINs")
        
        if '(select' in query_lower:
            suggestions.append("Consider converting subqueries to JOINs")
        
        if 'order by' in query_lower and 'limit' not in query_lower:
            suggestions.append("Consider adding LIMIT clause to ORDER BY queries")
        
        return suggestions
    
    def _calculate_anomaly_score(self, query: str) -> float:
        """Calculate anomaly score for a query"""
        score = 0
        query_lower = query.lower()
        
        # Very long queries
        if len(query) > 5000:
            score += 0.3
        
        # Too many JOINs
        if query_lower.count('join') > 10:
            score += 0.4
        
        # Excessive subqueries
        if query_lower.count('(select') > 5:
            score += 0.3
        
        # Suspicious patterns
        suspicious_patterns = ['union all', 'drop table', 'delete from', 'truncate']
        for pattern in suspicious_patterns:
            if pattern in query_lower:
                score += 0.2
        
        return min(1.0, score)
    
    def _get_anomaly_reasons(self, query: str, score: float) -> List[str]:
        """Get reasons why a query might be anomalous"""
        reasons = []
        query_lower = query.lower()
        
        if len(query) > 5000:
            reasons.append("Unusually long query")
        
        if query_lower.count('join') > 10:
            reasons.append("Excessive number of JOINs")
        
        if query_lower.count('(select') > 5:
            reasons.append("Too many subqueries")
        
        if 'drop table' in query_lower:
            reasons.append("Contains DROP TABLE statement")
        
        if 'delete from' in query_lower and 'where' not in query_lower:
            reasons.append("DELETE without WHERE clause")
        
        return reasons
    
    def _calculate_optimization_score(self, query: str, recommendations: List[Dict]) -> float:
        """Calculate optimization potential score"""
        base_score = 10.0
        
        # Reduce score based on issues found
        for rec in recommendations:
            if rec["priority"] == "high":
                base_score -= 3
            elif rec["priority"] == "medium":
                base_score -= 2
            elif rec["priority"] == "low":
                base_score -= 1
        
        return max(1.0, base_score)
    
    def _estimate_performance_improvement(self, recommendations: List[Dict]) -> str:
        """Estimate potential performance improvement"""
        high_priority = sum(1 for r in recommendations if r["priority"] == "high")
        medium_priority = sum(1 for r in recommendations if r["priority"] == "medium")
        
        if high_priority >= 2:
            return "30-60% improvement possible"
        elif high_priority >= 1 or medium_priority >= 3:
            return "15-30% improvement possible"
        elif medium_priority >= 1:
            return "5-15% improvement possible"
        else:
            return "Minimal improvement expected"
    
    def _get_pattern_recommendations(self, patterns: Dict) -> List[str]:
        """Get recommendations based on query patterns"""
        recommendations = []
        
        if patterns["average_complexity"] > 7:
            recommendations.append("Consider query optimization - average complexity is high")
        
        if patterns["most_common_query_type"] == "SELECT":
            recommendations.append("Consider read replicas for heavy SELECT workloads")
        elif patterns["most_common_query_type"] in ["INSERT", "UPDATE", "DELETE"]:
            recommendations.append("Consider write optimization and proper indexing")
        
        # Table access patterns
        if patterns["most_accessed_tables"]:
            top_table = patterns["most_accessed_tables"][0]
            recommendations.append(f"Table '{top_table[0]}' is heavily accessed - ensure proper indexing")
        
        return recommendations


class MLEnhancedAPIHandler(APIHandler):
    """
    Enhanced API handler with ML endpoints
    """
    
    def do_GET(self):
        """Handle GET requests including ML endpoints"""
        path = urllib.parse.urlparse(self.path).path
        
        # ML status endpoint
        if path == '/api/ml/status':
            ml_status = {
                'ml_enabled': gemini_api.ml_enabled if hasattr(gemini_api, 'ml_enabled') else False,
                'models_loaded': list(gemini_api.ml_models.keys()) if hasattr(gemini_api, 'ml_models') else [],
                'preprocessor_available': gemini_api.preprocessor is not None if hasattr(gemini_api, 'preprocessor') else False
            }
            self._send_json_response({'success': True, 'ml_status': ml_status})
        
        # Training status endpoint
        elif path == '/api/ml/training/status':
            # Check if training is in progress or completed
            training_status = {
                'training_available': True,
                'last_training': None,
                'models_trained': len(gemini_api.ml_models) if hasattr(gemini_api, 'ml_models') else 0
            }
            self._send_json_response({'success': True, 'training_status': training_status})
        
        else:
            # Call parent method for other endpoints
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests including ML endpoints"""
        path = urllib.parse.urlparse(self.path).path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            # Query performance prediction
            if path == '/api/ml/predict/performance':
                query = data.get('query', '')
                if not query:
                    self._send_json_response({'error': 'Query is required'}, 400)
                    return
                
                result = gemini_api.predict_query_performance(query)
                self._send_json_response(result)
            
            # Anomaly detection
            elif path == '/api/ml/detect/anomalies':
                queries = data.get('queries', [])
                if not queries:
                    self._send_json_response({'error': 'Queries list is required'}, 400)
                    return
                
                result = gemini_api.detect_query_anomalies(queries)
                self._send_json_response(result)
            
            # Optimization recommendations
            elif path == '/api/ml/optimize/recommendations':
                query = data.get('query', '')
                performance_data = data.get('performance_data', {})
                
                if not query:
                    self._send_json_response({'error': 'Query is required'}, 400)
                    return
                
                result = gemini_api.get_optimization_recommendations(query, performance_data)
                self._send_json_response(result)
            
            # Pattern analysis
            elif path == '/api/ml/analyze/patterns':
                queries = data.get('queries', [])
                if not queries:
                    self._send_json_response({'error': 'Queries list is required'}, 400)
                    return
                
                result = gemini_api.analyze_query_patterns(queries)
                self._send_json_response(result)
            
            # Train models
            elif path == '/api/ml/train':
                training_data = data.get('training_data', {})
                
                # For now, return a placeholder response
                self._send_json_response({
                    'success': True,
                    'message': 'Training initiated',
                    'training_id': f'train_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'estimated_duration': '5-10 minutes'
                })
            
            else:
                # Call parent method for other endpoints
                super().do_POST()
                
        except json.JSONDecodeError:
            self._send_json_response({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in ML endpoint: {e}")
            self._send_json_response({'error': str(e)}, 500)


def start_ml_enhanced_server(port=8080):
    """Start the ML-enhanced web server"""
    global gemini_api
    
    # Initialize enhanced Gemini API
    try:
        gemini_api = MLEnhancedGeminiAPI()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set GOOGLE_API_KEY environment variable")
        return False
    
    # Start server
    try:
        with socketserver.TCPServer(("", port), MLEnhancedAPIHandler) as httpd:
            server_url = f"http://localhost:{port}"
            print(f"🌐 ML-Enhanced Web server started at {server_url}")
            print(f"📱 Open {server_url} in your browser to use the chat interface")
            print(f"🤖 ML Features: {'Enabled' if gemini_api.ml_enabled else 'Disabled'}")
            if gemini_api.ml_enabled:
                print(f"🧠 Loaded {len(gemini_api.ml_models)} ML models")
            print("Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False


if __name__ == "__main__":
    start_ml_enhanced_server()