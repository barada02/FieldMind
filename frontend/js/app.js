/**
 * Field Mind - Frontend Application
 * Handles chat interface, WebSocket communication, and UI interactions
 */

class FieldMindApp {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.conversationId = null;
        this.ws = null;
        this.isConnected = false;
        
        // DOM elements
        this.elements = {
            chatMessages: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            sendButton: document.getElementById('sendButton'),
            clearButton: document.getElementById('clearChat'),
            typingIndicator: document.getElementById('typingIndicator'),
            welcomeMessage: document.getElementById('welcomeMessage'),
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.querySelector('.status-text')
        };
        
        this.init();
    }
    
    /**
     * Initialize the application
     */
    init() {
        this.setupEventListeners();
        this.checkHealth();
        this.connectWebSocket();
        this.autoResizeTextarea();
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Send message on button click
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter (Shift+Enter for new line)
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Clear chat
        this.elements.clearButton.addEventListener('click', () => this.clearChat());
        
        // Auto-resize textarea
        this.elements.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    }
    
    /**
     * Check API health status
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatus('connected', 'Connected');
            } else {
                this.updateStatus('error', 'Service Unavailable');
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.updateStatus('error', 'Connection Error');
        }
    }
    
    /**
     * Connect to WebSocket for real-time communication
     */
    connectWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws/chat`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.updateStatus('connected', 'Connected');
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus('error', 'Connection Error');
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.updateStatus('error', 'Disconnected');
                
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.updateStatus('error', 'Connection Failed');
        }
    }
    
    /**
     * Handle incoming WebSocket messages
     */
    handleWebSocketMessage(data) {
        if (data.type === 'message') {
            this.hideTypingIndicator();
            this.addMessage('assistant', data.content, data.sources);
        } else if (data.type === 'token') {
            // Handle streaming tokens (for future implementation)
            console.log('Streaming token:', data.content);
        }
    }
    
    /**
     * Send a message
     */
    async sendMessage() {
        const message = this.elements.messageInput.value.trim();
        
        if (!message) return;
        
        // Hide welcome message on first message
        if (this.elements.welcomeMessage) {
            this.elements.welcomeMessage.style.display = 'none';
        }
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        this.elements.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Disable send button
        this.elements.sendButton.disabled = true;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                // Send via WebSocket
                this.ws.send(JSON.stringify({ message }));
            } else {
                // Fallback to REST API
                await this.sendMessageViaAPI(message);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
        } finally {
            this.elements.sendButton.disabled = false;
        }
    }
    
    /**
     * Send message via REST API (fallback)
     */
    async sendMessageViaAPI(message) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message,
                    conversation_id: this.conversationId
                })
            });
            
            if (!response.ok) {
                throw new Error('API request failed');
            }
            
            const data = await response.json();
            this.conversationId = data.conversation_id;
            
            this.hideTypingIndicator();
            this.addMessage('assistant', data.message, data.sources);
        } catch (error) {
            console.error('API error:', error);
            throw error;
        }
    }
    
    /**
     * Add a message to the chat
     */
    addMessage(role, content, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? '👤' : '🤖';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = content;
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this.formatTime(new Date());
        
        messageContent.appendChild(bubble);
        messageContent.appendChild(time);
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            
            const sourcesTitle = document.createElement('h4');
            sourcesTitle.textContent = '📚 Sources:';
            sourcesDiv.appendChild(sourcesTitle);
            
            sources.forEach(source => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';
                sourceItem.textContent = `• ${source.title || source.name}`;
                sourcesDiv.appendChild(sourceItem);
            });
            
            messageContent.appendChild(sourcesDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.elements.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.elements.typingIndicator.style.display = 'none';
    }
    
    /**
     * Clear chat history
     */
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.elements.chatMessages.innerHTML = '';
            this.conversationId = null;
            
            if (this.elements.welcomeMessage) {
                this.elements.welcomeMessage.style.display = 'block';
            }
        }
    }
    
    /**
     * Update connection status
     */
    updateStatus(status, text) {
        this.elements.statusIndicator.className = `status-indicator ${status}`;
        this.elements.statusText.textContent = text;
    }
    
    /**
     * Auto-resize textarea based on content
     */
    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
    }
    
    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatMessages.parentElement.scrollTop = 
                this.elements.chatMessages.parentElement.scrollHeight;
        }, 100);
    }
    
    /**
     * Format time for display
     */
    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.fieldMindApp = new FieldMindApp();
});

// Made with Bob
