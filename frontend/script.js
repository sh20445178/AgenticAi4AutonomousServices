// Gemini AI Chat Frontend JavaScript

class GeminiChatApp {
    constructor() {
        this.apiEndpoint = 'http://localhost:8080/api';
        this.isConnected = false;
        this.temperature = 0.7;
        this.maxTokens = 1000;
        
        // DOM elements
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            typingIndicator: document.getElementById('typingIndicator'),
            statusIcon: document.getElementById('statusIcon'),
            statusText: document.getElementById('statusText'),
            modelInfo: document.getElementById('modelInfo'),
            charCount: document.getElementById('charCount'),
            temperatureSlider: document.getElementById('temperatureSlider'),
            temperatureValue: document.getElementById('temperatureValue'),
            maxTokensSlider: document.getElementById('maxTokensSlider'),
            maxTokensValue: document.getElementById('maxTokensValue'),
            newChatBtn: document.getElementById('newChatBtn'),
            clearHistoryBtn: document.getElementById('clearHistoryBtn'),
            exportChatBtn: document.getElementById('exportChatBtn'),
            toggleSidebarBtn: document.getElementById('toggleSidebarBtn'),
            sidebar: document.querySelector('.sidebar')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkApiStatus();
        this.setupSliders();
        this.setupPromptButtons();
        this.autoResizeTextarea();
    }
    
    setupEventListeners() {
        // Send message events
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
        
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.elements.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.autoResizeTextarea();
        });
        
        // Control buttons
        this.elements.newChatBtn.addEventListener('click', () => this.newChat());
        this.elements.clearHistoryBtn.addEventListener('click', () => this.clearHistory());
        this.elements.exportChatBtn.addEventListener('click', () => this.exportChat());
        this.elements.toggleSidebarBtn.addEventListener('click', () => this.toggleSidebar());
        
        // Settings sliders
        this.elements.temperatureSlider.addEventListener('input', (e) => {
            this.temperature = parseFloat(e.target.value);
            this.elements.temperatureValue.textContent = this.temperature;
        });
        
        this.elements.maxTokensSlider.addEventListener('input', (e) => {
            this.maxTokens = parseInt(e.target.value);
            this.elements.maxTokensValue.textContent = this.maxTokens;
        });
        
        // Window resize for responsive design
        window.addEventListener('resize', () => this.handleResize());
    }
    
    setupSliders() {
        this.elements.temperatureValue.textContent = this.temperature;
        this.elements.maxTokensValue.textContent = this.maxTokens;
    }
    
    setupPromptButtons() {
        const promptButtons = document.querySelectorAll('.prompt-btn');
        promptButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const prompt = btn.getAttribute('data-prompt');
                this.elements.messageInput.value = prompt;
                this.elements.messageInput.focus();
                this.autoResizeTextarea();
                this.updateCharCount();
            });
        });
    }
    
    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiEndpoint}/status`);
            const data = await response.json();
            
            if (data.success) {
                this.updateStatus(true, 'Connected');
                this.updateModelInfo(data.model);
                this.isConnected = true;
            } else {
                throw new Error('API not responding');
            }
        } catch (error) {
            this.updateStatus(false, 'Disconnected');
            this.isConnected = false;
            this.showToast('Unable to connect to AI service. Please ensure the backend is running.', 'error');
        }
    }
    
    updateStatus(connected, text) {
        this.elements.statusIcon.className = `fas fa-circle ${connected ? 'text-success' : 'text-danger'}`;
        this.elements.statusIcon.style.color = connected ? '#34a853' : '#ea4335';
        this.elements.statusText.textContent = text;
    }
    
    updateModelInfo(model) {
        const modelSpan = this.elements.modelInfo.querySelector('span');
        if (modelSpan) {
            modelSpan.textContent = this.formatModelName(model);
        }
    }
    
    formatModelName(model) {
        return model.replace('models/', '').replace('-', ' ').toUpperCase();
    }
    
    async sendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and reset size
        this.elements.messageInput.value = '';
        this.autoResizeTextarea();
        this.updateCharCount();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Disable send button
        this.elements.sendBtn.disabled = true;
        
        try {
            const response = await fetch(`${this.apiEndpoint}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    temperature: this.temperature,
                    maxTokens: this.maxTokens
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage(data.response, 'ai', message);
                this.showToast('Message sent successfully!', 'success', 2000);
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Sorry, I encountered an error processing your request. Please try again.', 'ai', message);
            this.showToast(`Error: ${error.message}`, 'error');
        } finally {
            this.hideTypingIndicator();
            this.elements.sendBtn.disabled = false;
            this.elements.messageInput.focus();
        }
    }
    
    addMessage(content, type, userInput = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = type === 'user' ? 'user-avatar' : 'ai-avatar custom-avatar';
        
        if (type === 'user') {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        } else {
            // Custom AI avatar with dynamic icon based on response type
            const responseType = this.detectResponseType(content, userInput);
            avatar.innerHTML = this.getAvatarForResponseType(responseType);
        }
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = this.formatMessage(content, userInput);
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Remove welcome message if it exists
        const welcomeMsg = document.querySelector('.welcome-message');
        if (welcomeMsg && this.elements.chatMessages.children.length > 2) {
            welcomeMsg.style.display = 'none';
        }
        
        // Add copy buttons to code blocks
        this.addCopyButtons(messageDiv);
    }
    
    detectResponseType(content, userInput = '') {
        const lowerContent = content.toLowerCase();
        const lowerInput = userInput.toLowerCase();
        
        // SQL Query responses
        if (this.containsSQLKeywords(lowerContent) || this.containsSQLKeywords(lowerInput)) {
            return 'sql';
        }
        
        // Code responses
        if (content.includes('```') || this.containsCodePatterns(content)) {
            return 'code';
        }
        
        // Table/structured data responses
        if (this.containsTablePatterns(content)) {
            return 'table';
        }
        
        // Schema/design responses
        if (lowerInput.includes('schema') || lowerInput.includes('design') || 
            lowerContent.includes('table') && lowerContent.includes('column')) {
            return 'schema';
        }
        
        // Performance/optimization responses
        if (lowerInput.includes('performance') || lowerInput.includes('optimize') ||
            lowerContent.includes('index') || lowerContent.includes('performance')) {
            return 'performance';
        }
        
        // Migration responses
        if (lowerInput.includes('migration') || lowerInput.includes('migrate')) {
            return 'migration';
        }
        
        // List/steps responses
        if (this.containsListPatterns(content)) {
            return 'list';
        }
        
        return 'general';
    }
    
    containsSQLKeywords(text) {
        const sqlKeywords = ['select', 'from', 'where', 'join', 'insert', 'update', 'delete', 
                           'create table', 'alter table', 'drop table', 'group by', 'order by',
                           'having', 'union', 'inner join', 'left join', 'right join'];
        return sqlKeywords.some(keyword => text.includes(keyword));
    }
    
    containsCodePatterns(content) {
        const codePatterns = [/function\s+\w+\s*\(/i, /class\s+\w+/i, /def\s+\w+\s*\(/i,
                             /import\s+\w+/i, /from\s+\w+\s+import/i, /var\s+\w+\s*=/i,
                             /let\s+\w+\s*=/i, /const\s+\w+\s*=/i];
        return codePatterns.some(pattern => pattern.test(content));
    }
    
    containsTablePatterns(content) {
        return content.includes('|') && content.includes('---') ||
               content.match(/\|\s*\w+\s*\|\s*\w+\s*\|/);
    }
    
    containsListPatterns(content) {
        return content.includes('\n1.') || content.includes('\n- ') || 
               content.includes('\n* ') || content.includes('\n•');
    }
    
    getAvatarForResponseType(responseType) {
        const avatarMap = {
            'sql': '<i class="fas fa-database" style="color: #4285f4;"></i>',
            'code': '<i class="fas fa-code" style="color: #34a853;"></i>',
            'table': '<i class="fas fa-table" style="color: #fbbc04;"></i>',
            'schema': '<i class="fas fa-sitemap" style="color: #ea4335;"></i>',
            'performance': '<i class="fas fa-tachometer-alt" style="color: #ff6d01;"></i>',
            'migration': '<i class="fas fa-exchange-alt" style="color: #9c27b0;"></i>',
            'list': '<i class="fas fa-list-ul" style="color: #607d8b;"></i>',
            'general': `<svg width="24" height="24" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                           <defs>
                               <linearGradient id="miniGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                   <stop offset="0%" style="stop-color:#4285f4;stop-opacity:1" />
                                   <stop offset="50%" style="stop-color:#34a853;stop-opacity:1" />
                                   <stop offset="100%" style="stop-color:#ea4335;stop-opacity:1" />
                               </linearGradient>
                           </defs>
                           <circle cx="50" cy="50" r="45" fill="url(#miniGradient)"/>
                           <circle cx="50" cy="50" r="35" fill="white" opacity="0.9"/>
                           <path d="M30 40 L70 40 L70 48 L30 48 Z M30 52 L60 52 L60 60 L30 60 Z M30 64 L70 64 L70 72 L30 72 Z" fill="url(#miniGradient)"/>
                       </svg>`
        };
        return avatarMap[responseType] || avatarMap['general'];
    }
    
    formatMessage(content, userInput = '') {
        const responseType = this.detectResponseType(content, userInput);
        
        // Pre-process content based on type
        let formatted = content;
        
        // Handle different response types
        switch (responseType) {
            case 'sql':
                formatted = this.formatSQLResponse(formatted);
                break;
            case 'code':
                formatted = this.formatCodeResponse(formatted);
                break;
            case 'table':
                formatted = this.formatTableResponse(formatted);
                break;
            case 'schema':
                formatted = this.formatSchemaResponse(formatted);
                break;
            case 'performance':
                formatted = this.formatPerformanceResponse(formatted);
                break;
            case 'list':
                formatted = this.formatListResponse(formatted);
                break;
            default:
                formatted = this.formatGeneralResponse(formatted);
        }
        
        return formatted;
    }
    
    formatSQLResponse(content) {
        let formatted = content;
        
        // Handle SQL code blocks with syntax highlighting
        formatted = formatted.replace(/```sql\n([\s\S]*?)\n```/gi, (match, code) => {
            return `<div class="sql-block">
                <div class="code-header">
                    <i class="fas fa-database"></i>
                    <span>SQL Query</span>
                    <button class="copy-btn" title="Copy SQL">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
                <div class="code-content">
                    <pre><code class="language-sql">${this.highlightSQL(code.trim())}</code></pre>
                </div>
            </div>`;
        });
        
        // Handle inline SQL keywords
        const sqlKeywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INSERT', 'UPDATE', 'DELETE', 
                           'CREATE', 'ALTER', 'DROP', 'INDEX', 'GROUP BY', 'ORDER BY'];
        sqlKeywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            formatted = formatted.replace(regex, `<span class="sql-keyword">${keyword}</span>`);
        });
        
        return this.formatGeneralResponse(formatted);
    }
    
    formatCodeResponse(content) {
        let formatted = content;
        
        // Enhanced code block formatting with language detection
        formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)\n```/gi, (match, lang, code) => {
            const language = lang || 'code';
            const icon = this.getLanguageIcon(language);
            
            return `<div class="code-block ${language}">
                <div class="code-header">
                    ${icon}
                    <span>${language.toUpperCase()}</span>
                    <button class="copy-btn" title="Copy Code">
                        <i class="fas fa-copy"></i>
                    </button>
                </div>
                <div class="code-content">
                    <pre><code class="language-${language}">${this.escapeHtml(code.trim())}</code></pre>
                </div>
            </div>`;
        });
        
        return this.formatGeneralResponse(formatted);
    }
    
    formatTableResponse(content) {
        let formatted = content;
        
        // Convert markdown tables to HTML
        formatted = formatted.replace(/\|(.+)\|\n\|[-:| ]+\|\n((?:\|.+\|\n?)*)/g, (match, header, rows) => {
            const headers = header.split('|').map(h => h.trim()).filter(h => h);
            const rowData = rows.trim().split('\n').map(row => 
                row.split('|').map(cell => cell.trim()).filter(cell => cell)
            );
            
            let tableHtml = `<div class="data-table-container">
                <div class="table-header">
                    <i class="fas fa-table"></i>
                    <span>Data Table</span>
                </div>
                <div class="table-wrapper">
                    <table class="data-table">
                        <thead><tr>`;
            
            headers.forEach(header => {
                tableHtml += `<th>${header}</th>`;
            });
            
            tableHtml += `</tr></thead><tbody>`;
            
            rowData.forEach(row => {
                tableHtml += '<tr>';
                row.forEach(cell => {
                    tableHtml += `<td>${cell}</td>`;
                });
                tableHtml += '</tr>';
            });
            
            tableHtml += '</tbody></table></div></div>';
            return tableHtml;
        });
        
        return this.formatGeneralResponse(formatted);
    }
    
    formatSchemaResponse(content) {
        let formatted = this.formatGeneralResponse(content);
        
        // Highlight table and column names
        formatted = formatted.replace(/\b([A-Z_][A-Z0-9_]*)\s+(?:TABLE|table)\b/g, 
            '<span class="schema-table">$1 TABLE</span>');
        formatted = formatted.replace(/\b([a-z_][a-z0-9_]*)\s+(?:VARCHAR|INT|TEXT|DATE|TIMESTAMP|BOOLEAN)/gi, 
            '<span class="schema-column">$1</span> <span class="schema-type">$2</span>');
        
        return formatted;
    }
    
    formatPerformanceResponse(content) {
        let formatted = this.formatGeneralResponse(content);
        
        // Highlight performance-related terms
        const perfTerms = ['INDEX', 'EXPLAIN', 'ANALYZE', 'PERFORMANCE', 'OPTIMIZATION', 'QUERY PLAN'];
        perfTerms.forEach(term => {
            const regex = new RegExp(`\\b${term}\\b`, 'gi');
            formatted = formatted.replace(regex, `<span class="perf-term">${term}</span>`);
        });
        
        return formatted;
    }
    
    formatListResponse(content) {
        let formatted = content;
        
        // Enhanced list formatting
        formatted = formatted.replace(/^(\d+\.\s+)(.*$)/gm, 
            '<li class="numbered-item"><span class="list-number">$1</span>$2</li>');
        formatted = formatted.replace(/^([-*•]\s+)(.*$)/gm, 
            '<li class="bullet-item"><span class="bullet">$1</span>$2</li>');
        
        // Wrap consecutive list items in appropriate containers
        formatted = formatted.replace(/((?:<li class="numbered-item">.*<\/li>\s*)+)/gs, 
            '<ol class="enhanced-list numbered">$1</ol>');
        formatted = formatted.replace(/((?:<li class="bullet-item">.*<\/li>\s*)+)/gs, 
            '<ul class="enhanced-list bulleted">$1</ul>');
        
        return this.formatGeneralResponse(formatted);
    }
    
    formatGeneralResponse(content) {
        // Basic markdown-like formatting
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
            .replace(/\n/g, '<br>');
        
        // Handle remaining code blocks
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>');
        
        return formatted;
    }
    
    highlightSQL(sql) {
        const keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
                         'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TABLE',
                         'INDEX', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET'];
        
        let highlighted = this.escapeHtml(sql);
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
            highlighted = highlighted.replace(regex, `<span class="sql-keyword">${keyword}</span>`);
        });
        
        return highlighted;
    }
    
    getLanguageIcon(language) {
        const icons = {
            'sql': '<i class="fas fa-database"></i>',
            'python': '<i class="fab fa-python"></i>',
            'javascript': '<i class="fab fa-js-square"></i>',
            'java': '<i class="fab fa-java"></i>',
            'php': '<i class="fab fa-php"></i>',
            'css': '<i class="fab fa-css3-alt"></i>',
            'html': '<i class="fab fa-html5"></i>',
            'json': '<i class="fas fa-code"></i>',
            'xml': '<i class="fas fa-code"></i>'
        };
        return icons[language.toLowerCase()] || '<i class="fas fa-code"></i>';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    addCopyButtons(messageDiv) {
        const copyButtons = messageDiv.querySelectorAll('.copy-btn');
        copyButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const codeBlock = btn.closest('.sql-block, .code-block');
                const code = codeBlock.querySelector('code').textContent;
                
                navigator.clipboard.writeText(code).then(() => {
                    const originalIcon = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-check"></i>';
                    btn.style.color = '#34a853';
                    
                    setTimeout(() => {
                        btn.innerHTML = originalIcon;
                        btn.style.color = '';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    this.showToast('Failed to copy to clipboard', 'error');
                });
            });
        });
    }
    
    showTypingIndicator() {
        this.elements.typingIndicator.classList.add('show');
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.elements.typingIndicator.classList.remove('show');
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
        }, 100);
    }
    
    updateCharCount() {
        const count = this.elements.messageInput.value.length;
        this.elements.charCount.textContent = `${count} characters`;
        
        if (count > 2000) {
            this.elements.charCount.style.color = '#ea4335';
        } else if (count > 1500) {
            this.elements.charCount.style.color = '#fbbc04';
        } else {
            this.elements.charCount.style.color = '#5f6368';
        }
    }
    
    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    async newChat() {
        const confirmed = confirm('Start a new chat? This will clear the current conversation.');
        if (confirmed) {
            await this.clearHistory();
            
            // Show welcome message again
            const welcomeMsg = document.querySelector('.welcome-message');
            if (welcomeMsg) {
                welcomeMsg.style.display = 'flex';
            }
            
            this.showToast('New chat started!', 'success');
        }
    }
    
    async clearHistory() {
        try {
            const response = await fetch(`${this.apiEndpoint}/clear`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Clear all messages except welcome
                const messages = this.elements.chatMessages.querySelectorAll('.message');
                messages.forEach(msg => msg.remove());
                
                this.showToast('Chat history cleared!', 'success');
            } else {
                throw new Error(data.error || 'Failed to clear history');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            this.showToast(`Error clearing history: ${error.message}`, 'error');
        }
    }
    
    exportChat() {
        const messages = this.elements.chatMessages.querySelectorAll('.message');
        let chatContent = 'Gemini AI Chat Export\\n';
        chatContent += `Exported on: ${new Date().toLocaleString()}\\n\\n`;
        
        messages.forEach(msg => {
            const isUser = msg.classList.contains('user');
            const content = msg.querySelector('.message-content div').textContent;
            const time = msg.querySelector('.message-time').textContent;
            
            chatContent += `[${time}] ${isUser ? 'You' : 'AI'}: ${content}\\n\\n`;
        });
        
        // Download as text file
        const blob = new Blob([chatContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gemini-chat-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Chat exported successfully!', 'success');
    }
    
    toggleSidebar() {
        this.elements.sidebar.classList.toggle('open');
    }
    
    handleResize() {
        if (window.innerWidth > 768) {
            this.elements.sidebar.classList.remove('open');
        }
    }
    
    showToast(message, type = 'info', duration = 5000) {
        const toastId = type === 'error' ? 'errorToast' : 'successToast';
        const messageId = type === 'error' ? 'errorMessage' : 'successMessage';
        
        const toast = document.getElementById(toastId);
        const messageEl = document.getElementById(messageId);
        
        messageEl.textContent = message;
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, duration);
    }
}

// Utility function to hide toast
function hideToast(toastId) {
    document.getElementById(toastId).classList.remove('show');
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.geminiChat = new GeminiChatApp();
});

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.geminiChat) {
        window.geminiChat.checkApiStatus();
    }
});

// Service Worker for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}