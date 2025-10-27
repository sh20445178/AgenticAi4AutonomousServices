/**
 * ML Dashboard Component for AgenticAI4DB
 * Handles ML predictions, analysis, and visualization
 */

class MLDashboard {
    constructor() {
        this.mlEnabled = false;
        this.loadedModels = [];
        this.currentQuery = '';
        this.init();
    }

    async init() {
        // Check ML status on initialization
        await this.checkMLStatus();
        this.setupEventListeners();
        this.createMLInterface();
    }

    async checkMLStatus() {
        try {
            const response = await fetch('/api/ml/status');
            const data = await response.json();
            
            if (data.success) {
                this.mlEnabled = data.ml_status.ml_enabled;
                this.loadedModels = data.ml_status.models_loaded || [];
                this.updateMLStatus();
            }
        } catch (error) {
            console.error('Error checking ML status:', error);
            this.mlEnabled = false;
            this.updateMLStatus();
        }
    }

    updateMLStatus() {
        const statusElement = document.getElementById('ml-status');
        if (statusElement) {
            if (this.mlEnabled) {
                statusElement.className = 'ml-status';
                statusElement.innerHTML = `
                    <strong>🧠 ML Features: Enabled</strong><br>
                    Models loaded: ${this.loadedModels.length}<br>
                    Available models: ${this.loadedModels.join(', ') || 'None'}
                `;
            } else {
                statusElement.className = 'ml-status disabled';
                statusElement.innerHTML = `
                    <strong>⚠️ ML Features: Disabled</strong><br>
                    Run setup_ml.py to enable ML features
                `;
            }
        }
    }

    createMLInterface() {
        const chatContainer = document.getElementById('chat-container');
        if (!chatContainer) return;

        // Create ML controls panel
        const mlPanel = document.createElement('div');
        mlPanel.id = 'ml-panel';
        mlPanel.innerHTML = `
            <div class="ml-controls">
                <h3>🧠 ML Analysis Tools</h3>
                <div id="ml-status" class="ml-status">Checking ML status...</div>
                
                <div class="query-input-container">
                    <textarea id="ml-query-input" placeholder="Enter SQL query for ML analysis...
Example: SELECT * FROM users WHERE age > 25 ORDER BY created_date DESC"></textarea>
                </div>
                
                <div class="ml-controls-grid">
                    <button class="ml-button" id="predict-performance" ${this.mlEnabled ? '' : 'disabled'}>
                        ⚡ Predict Performance
                    </button>
                    <button class="ml-button" id="detect-anomalies" ${this.mlEnabled ? '' : 'disabled'}>
                        🔍 Detect Anomalies
                    </button>
                    <button class="ml-button" id="get-recommendations" ${this.mlEnabled ? '' : 'disabled'}>
                        💡 Get Recommendations
                    </button>
                    <button class="ml-button" id="analyze-patterns" ${this.mlEnabled ? '' : 'disabled'}>
                        📊 Analyze Patterns
                    </button>
                </div>
                
                <div class="query-examples">
                    <h4>Example Queries:</h4>
                    <div class="example-query" data-query="SELECT * FROM users WHERE age > 25 ORDER BY created_date DESC LIMIT 100">
                        Complex SELECT with WHERE, ORDER BY, LIMIT
                    </div>
                    <div class="example-query" data-query="SELECT u.name, p.title, COUNT(*) as post_count FROM users u JOIN posts p ON u.id = p.user_id GROUP BY u.id, p.title HAVING COUNT(*) > 5">
                        Multi-table JOIN with GROUP BY and HAVING
                    </div>
                    <div class="example-query" data-query="UPDATE users SET last_login = NOW() WHERE id IN (SELECT user_id FROM sessions WHERE active = 1)">
                        Subquery UPDATE statement
                    </div>
                </div>
            </div>
            
            <div id="ml-results"></div>
        `;

        // Insert ML panel before chat messages
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            chatContainer.insertBefore(mlPanel, messagesContainer);
        }
    }

    setupEventListeners() {
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', () => {
            this.attachEventListeners();
        });
        
        // If DOM is already ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.attachEventListeners();
            });
        } else {
            this.attachEventListeners();
        }
    }

    attachEventListeners() {
        // ML button event listeners
        setTimeout(() => {
            const predictBtn = document.getElementById('predict-performance');
            const detectBtn = document.getElementById('detect-anomalies');
            const recommendBtn = document.getElementById('get-recommendations');
            const patternsBtn = document.getElementById('analyze-patterns');
            const queryInput = document.getElementById('ml-query-input');

            if (predictBtn) predictBtn.addEventListener('click', () => this.predictPerformance());
            if (detectBtn) detectBtn.addEventListener('click', () => this.detectAnomalies());
            if (recommendBtn) recommendBtn.addEventListener('click', () => this.getRecommendations());
            if (patternsBtn) patternsBtn.addEventListener('click', () => this.analyzePatterns());

            // Example query click handlers
            document.querySelectorAll('.example-query').forEach(example => {
                example.addEventListener('click', () => {
                    const query = example.getAttribute('data-query');
                    if (queryInput) {
                        queryInput.value = query;
                        this.currentQuery = query;
                    }
                });
            });

            // Query input change handler
            if (queryInput) {
                queryInput.addEventListener('input', (e) => {
                    this.currentQuery = e.target.value;
                });
            }
        }, 100);
    }

    getCurrentQuery() {
        const queryInput = document.getElementById('ml-query-input');
        return queryInput ? queryInput.value.trim() : this.currentQuery;
    }

    showLoading(container, message = 'Processing...') {
        container.innerHTML = `
            <div class="ml-loading">
                <div class="ml-spinner"></div>
                ${message}
            </div>
        `;
    }

    async predictPerformance() {
        const query = this.getCurrentQuery();
        if (!query) {
            this.showError('Please enter a SQL query');
            return;
        }

        const resultsContainer = document.getElementById('ml-results');
        this.showLoading(resultsContainer, 'Predicting query performance...');

        try {
            const response = await fetch('/api/ml/predict/performance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (data.success && data.prediction) {
                this.displayPerformancePrediction(data.prediction, query);
            } else {
                this.showError(data.error || 'Performance prediction failed');
            }
        } catch (error) {
            console.error('Performance prediction error:', error);
            this.showError('Network error during performance prediction');
        }
    }

    displayPerformancePrediction(prediction, query) {
        const resultsContainer = document.getElementById('ml-results');
        
        resultsContainer.innerHTML = `
            <div class="ml-result performance-result">
                <h4>⚡ Performance Prediction Results</h4>
                
                <div class="performance-metrics">
                    <div class="metric-card">
                        <div class="metric-value">${Math.round(prediction.predicted_execution_time_ms)}ms</div>
                        <div class="metric-label">Estimated Execution Time</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${prediction.query_complexity.toFixed(1)}/10</div>
                        <div class="metric-label">Complexity Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${prediction.query_type}</div>
                        <div class="metric-label">Query Type</div>
                    </div>
                </div>

                <h5>Resource Usage Prediction:</h5>
                <div class="performance-metrics">
                    <div class="metric-card">
                        <div class="metric-value">${Math.round(prediction.resource_usage_prediction.cpu_usage_percent)}%</div>
                        <div class="metric-label">CPU Usage</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${Math.round(prediction.resource_usage_prediction.memory_usage_mb)}MB</div>
                        <div class="metric-label">Memory Usage</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${prediction.resource_usage_prediction.disk_io_operations}</div>
                        <div class="metric-label">Disk I/O Ops</div>
                    </div>
                </div>

                ${prediction.optimization_suggestions.length > 0 ? `
                    <h5>Quick Optimization Suggestions:</h5>
                    <ul>
                        ${prediction.optimization_suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                ` : ''}

                <div style="margin-top: 15px; padding: 10px; background: rgba(0,123,255,0.1); border-radius: 4px; font-size: 12px;">
                    <strong>Query:</strong> ${query.length > 200 ? query.substring(0, 200) + '...' : query}
                </div>
            </div>
        `;
    }

    async detectAnomalies() {
        const query = this.getCurrentQuery();
        if (!query) {
            this.showError('Please enter a SQL query');
            return;
        }

        const resultsContainer = document.getElementById('ml-results');
        this.showLoading(resultsContainer, 'Detecting query anomalies...');

        try {
            const response = await fetch('/api/ml/detect/anomalies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ queries: [query] })
            });

            const data = await response.json();

            if (data.success) {
                this.displayAnomalyResults(data);
            } else {
                this.showError(data.error || 'Anomaly detection failed');
            }
        } catch (error) {
            console.error('Anomaly detection error:', error);
            this.showError('Network error during anomaly detection');
        }
    }

    displayAnomalyResults(data) {
        const resultsContainer = document.getElementById('ml-results');
        const anomalies = data.anomalies || [];
        
        resultsContainer.innerHTML = `
            <div class="ml-result anomaly-result">
                <h4>🔍 Anomaly Detection Results</h4>
                
                <div class="performance-metrics">
                    <div class="metric-card">
                        <div class="metric-value">${data.summary.total_queries}</div>
                        <div class="metric-label">Total Queries</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.summary.anomalous_queries}</div>
                        <div class="metric-label">Anomalous Queries</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${(data.summary.anomaly_rate * 100).toFixed(1)}%</div>
                        <div class="metric-label">Anomaly Rate</div>
                    </div>
                </div>

                <div class="anomaly-list">
                    ${anomalies.map(anomaly => `
                        <div class="anomaly-item ${anomaly.anomaly_score > 0.7 ? 'high-risk' : anomaly.anomaly_score > 0.4 ? 'medium-risk' : ''}">
                            <div>
                                <strong>Query ${anomaly.query_index + 1}</strong>
                                <span class="anomaly-score ${anomaly.anomaly_score > 0.7 ? 'high' : anomaly.anomaly_score > 0.4 ? 'medium' : 'low'}">
                                    ${(anomaly.anomaly_score * 100).toFixed(0)}% risk
                                </span>
                            </div>
                            <div style="margin: 8px 0; font-family: monospace; font-size: 12px; background: rgba(0,0,0,0.05); padding: 8px; border-radius: 4px;">
                                ${anomaly.query}
                            </div>
                            ${anomaly.reasons.length > 0 ? `
                                <div style="font-size: 12px; color: #666;">
                                    <strong>Reasons:</strong> ${anomaly.reasons.join(', ')}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    async getRecommendations() {
        const query = this.getCurrentQuery();
        if (!query) {
            this.showError('Please enter a SQL query');
            return;
        }

        const resultsContainer = document.getElementById('ml-results');
        this.showLoading(resultsContainer, 'Generating optimization recommendations...');

        try {
            const response = await fetch('/api/ml/optimize/recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (data.success) {
                this.displayRecommendations(data);
            } else {
                this.showError(data.error || 'Recommendation generation failed');
            }
        } catch (error) {
            console.error('Recommendations error:', error);
            this.showError('Network error during recommendation generation');
        }
    }

    displayRecommendations(data) {
        const resultsContainer = document.getElementById('ml-results');
        const recommendations = data.recommendations || [];
        
        resultsContainer.innerHTML = `
            <div class="ml-result optimization-result">
                <h4>💡 Optimization Recommendations</h4>
                
                <div class="performance-metrics">
                    <div class="metric-card">
                        <div class="metric-value">${data.optimization_score}/10</div>
                        <div class="metric-label">Optimization Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${recommendations.length}</div>
                        <div class="metric-label">Recommendations</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${data.estimated_improvement}</div>
                        <div class="metric-label">Est. Improvement</div>
                    </div>
                </div>

                ${recommendations.length > 0 ? `
                    <div class="recommendation-list">
                        ${recommendations.map(rec => `
                            <div class="recommendation-item ${rec.priority}-priority">
                                <div class="priority-badge ${rec.priority}">${rec.priority}</div>
                                <h5>${rec.suggestion}</h5>
                                <p>${rec.explanation}</p>
                                <small><strong>Type:</strong> ${rec.type}</small>
                            </div>
                        `).join('')}
                    </div>
                ` : '<p>No specific recommendations found - query appears well optimized!</p>'}

                <div style="margin-top: 15px; padding: 10px; background: rgba(40,167,69,0.1); border-radius: 4px; font-size: 12px;">
                    <strong>Analyzed Query:</strong> ${data.query}
                </div>
            </div>
        `;
    }

    async analyzePatterns() {
        const query = this.getCurrentQuery();
        if (!query) {
            this.showError('Please enter a SQL query (or multiple queries separated by semicolons)');
            return;
        }

        // Split queries by semicolon for pattern analysis
        const queries = query.split(';').map(q => q.trim()).filter(q => q.length > 0);

        const resultsContainer = document.getElementById('ml-results');
        this.showLoading(resultsContainer, 'Analyzing query patterns...');

        try {
            const response = await fetch('/api/ml/analyze/patterns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ queries })
            });

            const data = await response.json();

            if (data.success) {
                this.displayPatternAnalysis(data);
            } else {
                this.showError(data.error || 'Pattern analysis failed');
            }
        } catch (error) {
            console.error('Pattern analysis error:', error);
            this.showError('Network error during pattern analysis');
        }
    }

    displayPatternAnalysis(data) {
        const resultsContainer = document.getElementById('ml-results');
        const patterns = data.patterns || {};
        
        resultsContainer.innerHTML = `
            <div class="ml-result pattern-result">
                <h4>📊 Query Pattern Analysis</h4>
                
                <div class="performance-metrics">
                    <div class="metric-card">
                        <div class="metric-value">${data.total_queries}</div>
                        <div class="metric-label">Total Queries</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${patterns.most_common_query_type || 'N/A'}</div>
                        <div class="metric-label">Most Common Type</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${patterns.average_complexity ? patterns.average_complexity.toFixed(1) : 'N/A'}</div>
                        <div class="metric-label">Avg Complexity</div>
                    </div>
                </div>

                <div class="pattern-grid">
                    <div class="pattern-card">
                        <h5>Query Type Distribution</h5>
                        ${Object.entries(patterns.query_type_distribution || {}).map(([type, count]) => `
                            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                                <span>${type}</span>
                                <strong>${count}</strong>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="pattern-card">
                        <h5>Most Accessed Tables</h5>
                        ${(patterns.most_accessed_tables || []).slice(0, 5).map(([table, count]) => `
                            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                                <span>${table}</span>
                                <strong>${count} times</strong>
                            </div>
                        `).join('') || '<p>No tables identified</p>'}
                    </div>
                </div>

                ${data.recommendations && data.recommendations.length > 0 ? `
                    <h5>Pattern-Based Recommendations:</h5>
                    <ul>
                        ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;
    }

    showError(message) {
        const resultsContainer = document.getElementById('ml-results');
        resultsContainer.innerHTML = `
            <div class="ml-result" style="border-left-color: #dc3545; background: #f8d7da;">
                <h4>❌ Error</h4>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize ML Dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mlDashboard = new MLDashboard();
});

// Initialize immediately if DOM is already ready
if (document.readyState !== 'loading') {
    window.mlDashboard = new MLDashboard();
}