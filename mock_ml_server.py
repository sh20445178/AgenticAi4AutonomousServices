#!/usr/bin/env python3
"""
Mock ML Implementation for AgenticAI4DB Demo
Works without ML dependencies by providing realistic mock responses
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class MockMLPredictor:
    """Mock ML functionality for demonstration purposes"""
    
    def __init__(self):
        self.model_names = [
            'sklearn_performance_regressor',
            'sklearn_query_classifier', 
            'tensorflow_anomaly_detector',
            'tensorflow_optimization_recommender'
        ]
        self.ml_enabled = True
        
    def predict_query_performance(self, query: str) -> Dict[str, Any]:
        """Mock query performance prediction"""
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Generate realistic mock predictions based on query characteristics
        query_lower = query.lower()
        
        # Base execution time based on query complexity
        base_time = 50
        if 'join' in query_lower:
            base_time += query_lower.count('join') * 100
        if 'group by' in query_lower:
            base_time += 200
        if 'order by' in query_lower:
            base_time += 150
        if 'subquery' in query_lower or '(select' in query_lower:
            base_time += 300
        if len(query) > 500:
            base_time += len(query) // 10
            
        # Add some randomness
        execution_time = base_time + random.randint(-20, 50)
        
        # Calculate complexity score
        complexity = min(10, len(query) / 100 + query_lower.count('join') * 1.5 + 
                        query_lower.count('(select') * 2)
        
        # Determine query type
        if query_lower.strip().startswith('select'):
            query_type = 'SELECT'
        elif query_lower.strip().startswith('insert'):
            query_type = 'INSERT'
        elif query_lower.strip().startswith('update'):
            query_type = 'UPDATE'
        elif query_lower.strip().startswith('delete'):
            query_type = 'DELETE'
        else:
            query_type = 'OTHER'
            
        # Generate optimization suggestions
        suggestions = []
        if 'select *' in query_lower:
            suggestions.append("Replace SELECT * with specific column names")
        if query_lower.count('join') > 2:
            suggestions.append("Consider breaking down complex JOINs")
        if '(select' in query_lower:
            suggestions.append("Consider converting subqueries to JOINs")
        if 'where' in query_lower and 'index' not in query_lower:
            suggestions.append("Consider adding indexes on WHERE clause columns")
            
        return {
            "success": True,
            "prediction": {
                "predicted_execution_time_ms": float(execution_time),
                "query_complexity": round(complexity, 1),
                "optimization_suggestions": suggestions,
                "query_type": query_type,
                "resource_usage_prediction": {
                    "cpu_usage_percent": min(95, max(5, execution_time / 10 + random.randint(-10, 20))),
                    "memory_usage_mb": min(1000, max(10, execution_time / 5 + random.randint(-20, 50))),
                    "disk_io_operations": max(0, int(execution_time / 2 + random.randint(-10, 30)))
                }
            },
            "model_info": {
                "models_available": self.model_names,
                "preprocessor_loaded": True,
                "prediction_source": "mock_ml_engine"
            }
        }
    
    def detect_query_anomalies(self, queries: List[str]) -> Dict[str, Any]:
        """Mock anomaly detection"""
        
        time.sleep(0.3)
        
        anomalies = []
        for i, query in enumerate(queries):
            query_lower = query.lower()
            
            # Calculate mock anomaly score
            anomaly_score = 0.0
            
            # Check for anomaly indicators
            if len(query) > 2000:
                anomaly_score += 0.3
            if query_lower.count('join') > 8:
                anomaly_score += 0.4
            if query_lower.count('(select') > 3:
                anomaly_score += 0.2
            if 'drop table' in query_lower:
                anomaly_score += 0.8
            if 'delete from' in query_lower and 'where' not in query_lower:
                anomaly_score += 0.9
            if 'truncate' in query_lower:
                anomaly_score += 0.7
                
            # Add some randomness
            anomaly_score += random.uniform(0, 0.2)
            anomaly_score = min(1.0, anomaly_score)
            
            is_anomaly = anomaly_score > 0.6
            
            # Generate reasons
            reasons = []
            if len(query) > 2000:
                reasons.append("Unusually long query")
            if query_lower.count('join') > 8:
                reasons.append("Excessive number of JOINs")
            if query_lower.count('(select') > 3:
                reasons.append("Too many subqueries")
            if 'drop table' in query_lower:
                reasons.append("Contains DROP TABLE statement")
            if 'delete from' in query_lower and 'where' not in query_lower:
                reasons.append("DELETE without WHERE clause")
                
            anomalies.append({
                "query_index": i,
                "query": query[:100] + "..." if len(query) > 100 else query,
                "is_anomaly": is_anomaly,
                "anomaly_score": round(anomaly_score, 3),
                "reasons": reasons
            })
        
        anomalous_count = sum(1 for a in anomalies if a["is_anomaly"])
        
        return {
            "success": True,
            "anomalies": anomalies,
            "summary": {
                "total_queries": len(queries),
                "anomalous_queries": anomalous_count,
                "anomaly_rate": round(anomalous_count / len(queries), 3) if queries else 0
            }
        }
    
    def get_optimization_recommendations(self, query: str, performance_data: Dict = None) -> Dict[str, Any]:
        """Mock optimization recommendations"""
        
        time.sleep(0.4)
        
        recommendations = []
        query_lower = query.lower()
        
        # Generate recommendations based on query analysis
        if 'select *' in query_lower:
            recommendations.append({
                "type": "query_optimization",
                "priority": "medium",
                "suggestion": "Specify only needed columns instead of SELECT *",
                "explanation": "Selecting all columns can impact performance and network usage"
            })
        
        if 'where' in query_lower:
            recommendations.append({
                "type": "index",
                "priority": "high",
                "suggestion": "Consider adding indexes on WHERE clause columns",
                "explanation": "Proper indexing can significantly improve query performance"
            })
        
        join_count = query_lower.count('join')
        if join_count > 3:
            recommendations.append({
                "type": "query_rewrite",
                "priority": "medium",
                "suggestion": f"Consider optimizing {join_count} JOINs or using materialized views",
                "explanation": "Complex joins can be performance bottlenecks"
            })
        
        if '(select' in query_lower:
            recommendations.append({
                "type": "query_rewrite",
                "priority": "medium",
                "suggestion": "Consider converting subqueries to JOINs",
                "explanation": "JOINs are often more efficient than correlated subqueries"
            })
        
        if 'order by' in query_lower and 'limit' not in query_lower:
            recommendations.append({
                "type": "query_optimization", 
                "priority": "low",
                "suggestion": "Consider adding LIMIT clause to ORDER BY queries",
                "explanation": "Sorting large result sets without LIMIT can be expensive"
            })
        
        if performance_data and performance_data.get('execution_frequency', 0) > 10:
            recommendations.append({
                "type": "caching",
                "priority": "high",
                "suggestion": "Implement query result caching",
                "explanation": "Frequently executed queries benefit from result caching"
            })
        
        # Calculate optimization score
        base_score = 10.0
        for rec in recommendations:
            if rec["priority"] == "high":
                base_score -= 3
            elif rec["priority"] == "medium":
                base_score -= 2
            elif rec["priority"] == "low":
                base_score -= 1
        
        optimization_score = max(1.0, base_score)
        
        # Estimate improvement
        high_priority = sum(1 for r in recommendations if r["priority"] == "high")
        medium_priority = sum(1 for r in recommendations if r["priority"] == "medium")
        
        if high_priority >= 2:
            improvement = "30-60% improvement possible"
        elif high_priority >= 1 or medium_priority >= 3:
            improvement = "15-30% improvement possible"
        elif medium_priority >= 1:
            improvement = "5-15% improvement possible"
        else:
            improvement = "Query appears well optimized"
        
        return {
            "success": True,
            "query": query[:200] + "..." if len(query) > 200 else query,
            "recommendations": recommendations,
            "optimization_score": round(optimization_score, 1),
            "estimated_improvement": improvement
        }
    
    def analyze_query_patterns(self, queries: List[str]) -> Dict[str, Any]:
        """Mock query pattern analysis"""
        
        time.sleep(0.6)
        
        if not queries:
            return {"error": "No queries provided"}
        
        # Analyze query types
        query_types = {}
        complexity_scores = []
        table_usage = {}
        
        for query in queries:
            query_lower = query.lower().strip()
            
            # Classify query type
            if query_lower.startswith('select'):
                q_type = 'SELECT'
            elif query_lower.startswith('insert'):
                q_type = 'INSERT'
            elif query_lower.startswith('update'):
                q_type = 'UPDATE'
            elif query_lower.startswith('delete'):
                q_type = 'DELETE'
            elif query_lower.startswith('create'):
                q_type = 'CREATE'
            else:
                q_type = 'OTHER'
            
            query_types[q_type] = query_types.get(q_type, 0) + 1
            
            # Calculate complexity
            complexity = min(10, len(query) / 200 + query_lower.count('join') * 1.5 + 
                           query_lower.count('(select') * 2)
            complexity_scores.append(complexity)
            
            # Extract table names (simple pattern matching)
            import re
            tables = re.findall(r'\bfrom\s+(\w+)', query_lower)
            tables.extend(re.findall(r'\bjoin\s+(\w+)', query_lower))
            tables.extend(re.findall(r'\bupdate\s+(\w+)', query_lower))
            tables.extend(re.findall(r'\binsert\s+into\s+(\w+)', query_lower))
            
            for table in tables:
                table_usage[table] = table_usage.get(table, 0) + 1
        
        # Generate patterns
        patterns = {
            "most_common_query_type": max(query_types, key=query_types.get) if query_types else "Unknown",
            "average_complexity": round(sum(complexity_scores) / len(complexity_scores), 2) if complexity_scores else 0,
            "most_accessed_tables": sorted(table_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            "query_type_distribution": query_types
        }
        
        # Generate recommendations
        recommendations = []
        if patterns["average_complexity"] > 7:
            recommendations.append("Consider query optimization - average complexity is high")
        
        if patterns["most_common_query_type"] == "SELECT":
            recommendations.append("Consider read replicas for heavy SELECT workloads")
        elif patterns["most_common_query_type"] in ["INSERT", "UPDATE", "DELETE"]:
            recommendations.append("Consider write optimization and proper indexing")
        
        if patterns["most_accessed_tables"]:
            top_table = patterns["most_accessed_tables"][0]
            recommendations.append(f"Table '{top_table[0]}' is heavily accessed - ensure proper indexing")
        
        return {
            "success": True,
            "total_queries": len(queries),
            "patterns": patterns,
            "recommendations": recommendations
        }


# Create a mock-enabled version of the ML server
def create_mock_ml_server():
    """Create ML server with mock functionality"""
    
    # Import the base web server
    import sys
    import os
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    try:
        from web_server import GeminiWebAPI, APIHandler, start_web_server
        import socketserver
        import urllib.parse
        import http.server
        import json
        
        # Create enhanced API class with mock ML
        class MockMLEnhancedAPI(GeminiWebAPI):
            def __init__(self, api_key: str = None):
                super().__init__(api_key)
                self.ml_predictor = MockMLPredictor()
                self.ml_enabled = True
                self.ml_models = self.ml_predictor.model_names
                
            def predict_query_performance(self, query: str) -> Dict[str, Any]:
                return self.ml_predictor.predict_query_performance(query)
                
            def detect_query_anomalies(self, queries: List[str]) -> Dict[str, Any]:
                return self.ml_predictor.detect_query_anomalies(queries)
                
            def get_optimization_recommendations(self, query: str, performance_data: Dict = None) -> Dict[str, Any]:
                return self.ml_predictor.get_optimization_recommendations(query, performance_data)
                
            def analyze_query_patterns(self, queries: List[str]) -> Dict[str, Any]:
                return self.ml_predictor.analyze_query_patterns(queries)
        
        # Enhanced API handler with ML endpoints
        class MockMLAPIHandler(APIHandler):
            def do_GET(self):
                path = urllib.parse.urlparse(self.path).path
                
                if path == '/api/ml/status':
                    ml_status = {
                        'ml_enabled': True,
                        'models_loaded': gemini_api.ml_models,
                        'preprocessor_available': True,
                        'mock_mode': True
                    }
                    self._send_json_response({'success': True, 'ml_status': ml_status})
                else:
                    super().do_GET()
            
            def do_POST(self):
                path = urllib.parse.urlparse(self.path).path
                
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode('utf-8')
                    data = json.loads(post_data)
                    
                    if path == '/api/ml/predict/performance':
                        query = data.get('query', '')
                        if not query:
                            self._send_json_response({'error': 'Query is required'}, 400)
                            return
                        result = gemini_api.predict_query_performance(query)
                        self._send_json_response(result)
                    
                    elif path == '/api/ml/detect/anomalies':
                        queries = data.get('queries', [])
                        if not queries:
                            self._send_json_response({'error': 'Queries list is required'}, 400)
                            return
                        result = gemini_api.detect_query_anomalies(queries)
                        self._send_json_response(result)
                    
                    elif path == '/api/ml/optimize/recommendations':
                        query = data.get('query', '')
                        performance_data = data.get('performance_data', {})
                        if not query:
                            self._send_json_response({'error': 'Query is required'}, 400)
                            return
                        result = gemini_api.get_optimization_recommendations(query, performance_data)
                        self._send_json_response(result)
                    
                    elif path == '/api/ml/analyze/patterns':
                        queries = data.get('queries', [])
                        if not queries:
                            self._send_json_response({'error': 'Queries list is required'}, 400)
                            return
                        result = gemini_api.analyze_query_patterns(queries)
                        self._send_json_response(result)
                    
                    else:
                        super().do_POST()
                        
                except json.JSONDecodeError:
                    self._send_json_response({'error': 'Invalid JSON'}, 400)
                except Exception as e:
                    self._send_json_response({'error': str(e)}, 500)
        
        return MockMLEnhancedAPI, MockMLAPIHandler
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None, None


def start_mock_ml_server(port=8080):
    """Start the mock ML-enhanced server"""
    
    import socketserver
    
    try:
        # Get the mock classes
        MockMLEnhancedAPI, MockMLAPIHandler = create_mock_ml_server()
        
        if not MockMLEnhancedAPI:
            print("❌ Could not create mock ML server")
            return False
        
        # Initialize enhanced API
        global gemini_api
        try:
            gemini_api = MockMLEnhancedAPI()
        except ValueError as e:
            print(f"⚠️  Warning: {e}")
            print("   ML features will work, but AI responses may be limited")
            gemini_api = MockMLEnhancedAPI(api_key="mock_key")
        
        # Start server
        with socketserver.TCPServer(("", port), MockMLAPIHandler) as httpd:
            server_url = f"http://localhost:{port}"
            print()
            print("🎉 AgenticAI4DB Mock ML Server Started Successfully!")
            print("=" * 60)
            print(f"🌐 Server URL: {server_url}")
            print("🧠 ML Features: ENABLED (Mock Mode)")
            print(f"🤖 Mock Models: {len(gemini_api.ml_models)} available")
            print("📊 All ML endpoints functional with realistic demo data")
            print()
            print("🔧 Features Available:")
            print("   • Query Performance Prediction")
            print("   • Anomaly Detection") 
            print("   • Optimization Recommendations")
            print("   • Query Pattern Analysis")
            print("   • Enhanced Response Formatting")
            print()
            print("📱 Open the URL above in your browser to test")
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n👋 Server stopped")
                return True
                
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False


if __name__ == "__main__":
    start_mock_ml_server()