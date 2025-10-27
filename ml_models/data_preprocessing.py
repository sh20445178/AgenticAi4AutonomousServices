"""
Data preprocessing utilities for AgenticAI4DB ML models
Handles database performance metrics, query patterns, and schema analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import re
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabasePreprocessor:
    """
    Comprehensive data preprocessing for database-related ML tasks
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.vectorizers = {}
        self.feature_names = []
        
    def preprocess_query_features(self, queries: List[str]) -> np.ndarray:
        """
        Extract features from SQL queries for ML models
        
        Args:
            queries: List of SQL query strings
            
        Returns:
            Feature matrix for queries
        """
        logger.info(f"Processing {len(queries)} SQL queries for feature extraction")
        
        features = []
        for query in queries:
            query_features = self._extract_query_features(query)
            features.append(query_features)
        
        return np.array(features)
    
    def _extract_query_features(self, query: str) -> List[float]:
        """Extract numerical features from a single SQL query"""
        query_lower = query.lower().strip()
        
        features = [
            # Query complexity features
            len(query),  # Query length
            query_lower.count('select'),  # Number of SELECT statements
            query_lower.count('join'),  # Number of JOINs
            query_lower.count('where'),  # Number of WHERE clauses
            query_lower.count('group by'),  # Number of GROUP BY
            query_lower.count('order by'),  # Number of ORDER BY
            query_lower.count('having'),  # Number of HAVING clauses
            query_lower.count('union'),  # Number of UNION operations
            query_lower.count('subquery') + query_lower.count('(select'),  # Subqueries
            
            # Table and column counts (estimated)
            len(re.findall(r'\bfrom\s+(\w+)', query_lower)),  # Tables referenced
            len(re.findall(r'\b\w+\.\w+\b', query_lower)),  # Column references
            
            # Aggregation functions
            query_lower.count('count('),
            query_lower.count('sum('),
            query_lower.count('avg('),
            query_lower.count('max('),
            query_lower.count('min('),
            
            # Query type indicators (binary features)
            1.0 if 'insert' in query_lower else 0.0,
            1.0 if 'update' in query_lower else 0.0,
            1.0 if 'delete' in query_lower else 0.0,
            1.0 if 'create' in query_lower else 0.0,
            1.0 if 'alter' in query_lower else 0.0,
            1.0 if 'drop' in query_lower else 0.0,
        ]
        
        return features
    
    def preprocess_performance_metrics(self, metrics_df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """
        Preprocess database performance metrics
        
        Args:
            metrics_df: DataFrame with performance metrics columns
            
        Returns:
            Processed feature matrix and feature names
        """
        logger.info(f"Processing performance metrics with shape {metrics_df.shape}")
        
        # Handle missing values
        metrics_df = metrics_df.fillna(0)
        
        # Separate numerical and categorical columns
        numerical_cols = metrics_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = metrics_df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        processed_features = []
        feature_names = []
        
        # Process numerical features
        if numerical_cols:
            scaler = StandardScaler()
            numerical_features = scaler.fit_transform(metrics_df[numerical_cols])
            processed_features.append(numerical_features)
            feature_names.extend([f"num_{col}" for col in numerical_cols])
            self.scalers['performance_numerical'] = scaler
        
        # Process categorical features
        if categorical_cols:
            encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            categorical_features = encoder.fit_transform(metrics_df[categorical_cols])
            processed_features.append(categorical_features)
            
            # Get feature names from encoder
            cat_feature_names = []
            for i, col in enumerate(categorical_cols):
                categories = encoder.categories_[i]
                cat_feature_names.extend([f"cat_{col}_{cat}" for cat in categories])
            feature_names.extend(cat_feature_names)
            self.encoders['performance_categorical'] = encoder
        
        # Combine all features
        if processed_features:
            final_features = np.hstack(processed_features)
        else:
            final_features = np.array([]).reshape(len(metrics_df), 0)
        
        self.feature_names = feature_names
        return final_features, feature_names
    
    def preprocess_schema_data(self, schema_data: List[Dict]) -> np.ndarray:
        """
        Preprocess database schema information for ML models
        
        Args:
            schema_data: List of dictionaries containing schema information
            
        Returns:
            Feature matrix for schema analysis
        """
        logger.info(f"Processing {len(schema_data)} schema elements")
        
        features = []
        for schema_item in schema_data:
            schema_features = self._extract_schema_features(schema_item)
            features.append(schema_features)
        
        return np.array(features)
    
    def _extract_schema_features(self, schema_item: Dict) -> List[float]:
        """Extract features from schema information"""
        features = [
            # Table-level features
            len(schema_item.get('columns', [])),  # Number of columns
            len(schema_item.get('indexes', [])),  # Number of indexes
            len(schema_item.get('foreign_keys', [])),  # Number of foreign keys
            len(schema_item.get('constraints', [])),  # Number of constraints
            
            # Data type distribution
            sum(1 for col in schema_item.get('columns', []) 
                if col.get('type', '').lower() in ['int', 'integer', 'bigint']),  # Integer columns
            sum(1 for col in schema_item.get('columns', []) 
                if col.get('type', '').lower() in ['varchar', 'text', 'char']),  # String columns
            sum(1 for col in schema_item.get('columns', []) 
                if col.get('type', '').lower() in ['date', 'datetime', 'timestamp']),  # Date columns
            sum(1 for col in schema_item.get('columns', []) 
                if col.get('type', '').lower() in ['decimal', 'float', 'double']),  # Numeric columns
            
            # Nullable columns ratio
            sum(1 for col in schema_item.get('columns', []) 
                if col.get('nullable', True)) / max(len(schema_item.get('columns', [])), 1),
            
            # Primary key indicator
            1.0 if any(col.get('primary_key', False) for col in schema_item.get('columns', [])) else 0.0,
        ]
        
        return features
    
    def create_training_data(self, 
                           queries: List[str], 
                           performance_metrics: pd.DataFrame,
                           target_column: str,
                           test_size: float = 0.2,
                           random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Create training and testing datasets
        
        Args:
            queries: List of SQL queries
            performance_metrics: DataFrame with performance data
            target_column: Name of target column in performance_metrics
            test_size: Fraction of data for testing
            random_state: Random state for reproducibility
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        logger.info("Creating training and testing datasets")
        
        # Extract query features
        query_features = self.preprocess_query_features(queries)
        
        # Extract performance features (excluding target)
        feature_cols = [col for col in performance_metrics.columns if col != target_column]
        perf_features, _ = self.preprocess_performance_metrics(performance_metrics[feature_cols])
        
        # Combine features
        if query_features.shape[0] != perf_features.shape[0]:
            min_samples = min(query_features.shape[0], perf_features.shape[0])
            query_features = query_features[:min_samples]
            perf_features = perf_features[:min_samples]
            performance_metrics = performance_metrics.iloc[:min_samples]
        
        X = np.hstack([query_features, perf_features])
        y = performance_metrics[target_column].values
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=None
        )
        
        logger.info(f"Training set size: {X_train.shape}, Testing set size: {X_test.shape}")
        
        return X_train, X_test, y_train, y_test
    
    def vectorize_queries_for_similarity(self, queries: List[str]) -> np.ndarray:
        """
        Create TF-IDF vectors for query similarity analysis
        
        Args:
            queries: List of SQL queries
            
        Returns:
            TF-IDF matrix
        """
        logger.info(f"Creating TF-IDF vectors for {len(queries)} queries")
        
        # Preprocess queries for TF-IDF
        processed_queries = [self._preprocess_query_text(query) for query in queries]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # Keep SQL keywords
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform(processed_queries)
        self.vectorizers['query_similarity'] = vectorizer
        
        return tfidf_matrix.toarray()
    
    def _preprocess_query_text(self, query: str) -> str:
        """Preprocess query text for TF-IDF analysis"""
        # Convert to lowercase
        query = query.lower()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Remove comments
        query = re.sub(r'--.*?\n', ' ', query)
        query = re.sub(r'/\*.*?\*/', ' ', query, flags=re.DOTALL)
        
        # Normalize string literals
        query = re.sub(r"'[^']*'", "'STRING'", query)
        query = re.sub(r'"[^"]*"', '"STRING"', query)
        
        # Normalize numbers
        query = re.sub(r'\b\d+\.?\d*\b', 'NUMBER', query)
        
        return query.strip()
    
    def generate_synthetic_data(self, n_samples: int = 1000) -> Tuple[List[str], pd.DataFrame]:
        """
        Generate synthetic database data for testing ML models
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            List of synthetic queries and performance metrics DataFrame
        """
        logger.info(f"Generating {n_samples} synthetic database samples")
        
        np.random.seed(42)
        
        # Generate synthetic SQL queries
        query_templates = [
            "SELECT * FROM users WHERE age > {age} AND city = '{city}'",
            "SELECT COUNT(*) FROM orders WHERE order_date > '{date}' GROUP BY customer_id",
            "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE o.total > {amount}",
            "INSERT INTO products (name, price, category) VALUES ('{name}', {price}, '{category}')",
            "UPDATE inventory SET quantity = {qty} WHERE product_id = {id}",
            "DELETE FROM sessions WHERE last_activity < '{date}'",
        ]
        
        cities = ['New York', 'London', 'Tokyo', 'Paris', 'Sydney']
        categories = ['Electronics', 'Clothing', 'Books', 'Food', 'Sports']
        names = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
        
        queries = []
        for _ in range(n_samples):
            template = np.random.choice(query_templates)
            query = template.format(
                age=np.random.randint(18, 80),
                city=np.random.choice(cities),
                date=f"2024-{np.random.randint(1, 13):02d}-{np.random.randint(1, 29):02d}",
                amount=np.random.randint(10, 1000),
                name=np.random.choice(names),
                price=round(np.random.uniform(10, 500), 2),
                category=np.random.choice(categories),
                qty=np.random.randint(1, 100),
                id=np.random.randint(1, 1000)
            )
            queries.append(query)
        
        # Generate synthetic performance metrics
        performance_data = {
            'execution_time_ms': np.random.lognormal(3, 1, n_samples),  # Log-normal distribution
            'cpu_usage_percent': np.random.uniform(5, 95, n_samples),
            'memory_usage_mb': np.random.uniform(10, 1000, n_samples),
            'rows_examined': np.random.randint(1, 1000000, n_samples),
            'rows_returned': np.random.randint(1, 10000, n_samples),
            'disk_io_operations': np.random.randint(0, 1000, n_samples),
            'cache_hit_ratio': np.random.uniform(0.5, 1.0, n_samples),
            'query_complexity_score': np.random.uniform(1, 10, n_samples),
            'table_count': np.random.randint(1, 10, n_samples),
            'index_usage': np.random.choice(['Full', 'Partial', 'None'], n_samples),
            'query_type': [self._get_query_type(q) for q in queries],
        }
        
        performance_df = pd.DataFrame(performance_data)
        
        # Add some correlation between features
        performance_df['execution_time_ms'] *= (1 + performance_df['query_complexity_score'] / 10)
        performance_df['cpu_usage_percent'] += performance_df['execution_time_ms'] / 100
        
        return queries, performance_df
    
    def _get_query_type(self, query: str) -> str:
        """Determine query type from SQL string"""
        query_lower = query.lower().strip()
        if query_lower.startswith('select'):
            return 'SELECT'
        elif query_lower.startswith('insert'):
            return 'INSERT'
        elif query_lower.startswith('update'):
            return 'UPDATE'
        elif query_lower.startswith('delete'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def save_preprocessor(self, filepath: str):
        """Save preprocessor state"""
        import joblib
        
        state = {
            'scalers': self.scalers,
            'encoders': self.encoders,
            'vectorizers': self.vectorizers,
            'feature_names': self.feature_names
        }
        
        joblib.dump(state, filepath)
        logger.info(f"Preprocessor saved to {filepath}")
    
    def load_preprocessor(self, filepath: str):
        """Load preprocessor state"""
        import joblib
        
        state = joblib.load(filepath)
        self.scalers = state['scalers']
        self.encoders = state['encoders']
        self.vectorizers = state['vectorizers']
        self.feature_names = state['feature_names']
        
        logger.info(f"Preprocessor loaded from {filepath}")


class QueryPatternAnalyzer:
    """
    Specialized analyzer for SQL query patterns and anomalies
    """
    
    def __init__(self):
        self.pattern_vectorizer = None
        self.common_patterns = []
    
    def extract_query_patterns(self, queries: List[str]) -> List[Dict]:
        """
        Extract common patterns from SQL queries
        
        Args:
            queries: List of SQL queries
            
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        
        for query in queries:
            pattern = {
                'original_query': query,
                'normalized_query': self._normalize_query(query),
                'query_type': self._get_query_type(query),
                'tables_accessed': self._extract_tables(query),
                'columns_accessed': self._extract_columns(query),
                'join_count': query.lower().count('join'),
                'subquery_count': query.lower().count('(select'),
                'aggregate_functions': self._extract_aggregates(query),
                'complexity_score': self._calculate_complexity(query)
            }
            patterns.append(pattern)
        
        return patterns
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query by removing literals and standardizing format"""
        normalized = query.lower()
        
        # Replace string literals
        normalized = re.sub(r"'[^']*'", '?', normalized)
        normalized = re.sub(r'"[^"]*"', '?', normalized)
        
        # Replace numeric literals
        normalized = re.sub(r'\b\d+\.?\d*\b', '?', normalized)
        
        # Standardize whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from query"""
        query_lower = query.lower()
        
        # Find tables after FROM clause
        from_matches = re.findall(r'\bfrom\s+(\w+)', query_lower)
        
        # Find tables after JOIN clause
        join_matches = re.findall(r'\bjoin\s+(\w+)', query_lower)
        
        # Find tables after UPDATE clause
        update_matches = re.findall(r'\bupdate\s+(\w+)', query_lower)
        
        # Find tables after INSERT INTO clause
        insert_matches = re.findall(r'\binsert\s+into\s+(\w+)', query_lower)
        
        all_tables = from_matches + join_matches + update_matches + insert_matches
        return list(set(all_tables))
    
    def _extract_columns(self, query: str) -> List[str]:
        """Extract column references from query"""
        # This is a simplified extraction - in practice, you'd need a proper SQL parser
        column_pattern = r'\b\w+\.\w+\b'
        columns = re.findall(column_pattern, query.lower())
        return list(set(columns))
    
    def _extract_aggregates(self, query: str) -> List[str]:
        """Extract aggregate functions from query"""
        query_lower = query.lower()
        aggregates = []
        
        agg_functions = ['count', 'sum', 'avg', 'max', 'min', 'group_concat']
        for func in agg_functions:
            if f'{func}(' in query_lower:
                aggregates.append(func)
        
        return aggregates
    
    def _calculate_complexity(self, query: str) -> float:
        """Calculate query complexity score"""
        query_lower = query.lower()
        
        complexity = 0
        complexity += len(query) / 100  # Base complexity from length
        complexity += query_lower.count('join') * 2  # JOINs add complexity
        complexity += query_lower.count('(select') * 3  # Subqueries add more complexity
        complexity += query_lower.count('union') * 2  # UNIONs add complexity
        complexity += len(re.findall(r'\bwhere\b', query_lower)) * 1.5  # WHERE clauses
        complexity += len(re.findall(r'\bgroup by\b', query_lower)) * 1.5  # GROUP BY
        complexity += len(re.findall(r'\border by\b', query_lower)) * 1  # ORDER BY
        
        return round(complexity, 2)
    
    def _get_query_type(self, query: str) -> str:
        """Get the type of SQL query"""
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


if __name__ == "__main__":
    # Example usage
    preprocessor = DatabasePreprocessor()
    
    # Generate synthetic data for testing
    queries, performance_df = preprocessor.generate_synthetic_data(100)
    
    print("Sample queries:")
    for i, query in enumerate(queries[:3]):
        print(f"{i+1}. {query}")
    
    print(f"\nPerformance data shape: {performance_df.shape}")
    print(f"Performance data columns: {performance_df.columns.tolist()}")
    print(f"\nSample performance metrics:")
    print(performance_df.head())
    
    # Test preprocessing
    X_train, X_test, y_train, y_test = preprocessor.create_training_data(
        queries, performance_df, 'execution_time_ms'
    )
    
    print(f"\nTraining data shape: {X_train.shape}")
    print(f"Testing data shape: {X_test.shape}")