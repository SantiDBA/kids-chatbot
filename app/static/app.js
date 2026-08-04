/**
 * CHAT-O - Frontend JavaScript
 * Vanilla JS, no dependencies, XSS-safe
 */

(function() {
    'use strict';

    // DOM elements
    const messagesArea = document.getElementById('messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const suggestionChips = document.querySelectorAll('.chip');
    const emptyState = document.getElementById('empty-state');

    // State
    let history = [];
    let isProcessing = false;

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Load history from localStorage on init
     */
    function loadHistory() {
        try {
            const saved = localStorage.getItem('chat-o-history');
            if (saved) {
                history = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Failed to load history from localStorage:', e);
        }
    }

    /**
     * Save history to localStorage
     */
    function saveHistory() {
        try {
            localStorage.setItem('chat-o-history', JSON.stringify(history));
        } catch (e) {
            console.warn('Failed to save history to localStorage:', e);
        }
    }

    /**
     * Clear empty state and show messages area
     */
    function hideEmptyState() {
        if (emptyState) {
            emptyState.style.display = 'none';
        }
    }

    /**
     * Scroll messages to bottom
     */
    function scrollToBottom() {
        messagesArea.scrollTop = messagesArea.scrollHeight;
    }

    /**
     * Append user message bubble
     */
    function appendUserMessage(text) {
        const bubble = document.createElement('div');
        bubble.className = 'message user';
        bubble.innerHTML = escapeHtml(text);
        messagesArea.appendChild(bubble);
        scrollToBottom();
    }

    /**
     * Append assistant message bubble
     */
    function appendAssistantMessage(text) {
        const bubble = document.createElement('div');
        bubble.className = 'message assistant';
        // Use textContent for safety, then set innerHTML only if we want formatting
        bubble.textContent = text;
        messagesArea.appendChild(bubble);
        scrollToBottom();
    }

    /**
     * Show typing indicator
     */
    function showTyping() {
        typingIndicator.classList.remove('hidden');
        messagesArea.appendChild(typingIndicator);
        scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    function hideTyping() {
        typingIndicator.classList.add('hidden');
    }

    /**
     * Send message to API
     */
    async function sendMessage(message, historyList) {
        // Append user message
        appendUserMessage(message);
        
        // Show typing indicator
        showTyping();
        
        // Disable input and button
        userInput.disabled = true;
        sendBtn.disabled = true;
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    history: historyList,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Read SSE stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';
            let fullReply = '';
            let streamDone = false;

            // Process one complete SSE event (ends with blank line)
            function handleEvent(eventText) {
                const lines = eventText.split('\n');
                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const payload = line.slice(6);
                    if (payload === '[DONE]') {
                        streamDone = true;
                        return;
                    }
                    let data = null;
                    try {
                        data = JSON.parse(payload);
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        if (data.reply) {
                            fullReply += data.reply;
                        }
                    } catch (parseError) {
                        if (data && parseError instanceof Error && parseError.message === data.error) {
                            throw parseError;
                        }
                        console.warn('Failed to parse SSE data:', parseError, payload);
                    }
                }
            }

            while (!streamDone) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                let eventEnd;
                while ((eventEnd = buffer.indexOf('\n\n')) !== -1) {
                    const eventText = buffer.slice(0, eventEnd);
                    buffer = buffer.slice(eventEnd + 2);
                    if (eventText.trim()) {
                        handleEvent(eventText);
                    }
                }
            }

            // Hide typing indicator
            hideTyping();
            
            // Append assistant response
            appendAssistantMessage(fullReply);
            
            // Update history
            history.push([message, fullReply]);
            saveHistory();
            
        } catch (error) {
            console.error('Chat error:', error);
            
            // Hide typing indicator
            hideTyping();
            
            // Show error message
            const errorBubble = document.createElement('div');
            errorBubble.className = 'message assistant';
            errorBubble.style.background = '#ff7675';
            errorBubble.style.color = 'white';
            errorBubble.textContent = `¡Uy! Hubo un problema: ${error.message}`;
            messagesArea.appendChild(errorBubble);
            
        } finally {
            // Re-enable input and button
            userInput.disabled = false;
            sendBtn.disabled = false;
            
            // Focus back on input
            userInput.focus();
        }
    }

    /**
     * Handle suggestion chip click
     */
    function handleSuggestion(message) {
        userInput.value = message;
        userInput.focus();
        
        // Auto-submit after a short delay
        setTimeout(() => {
            if (!userInput.disabled) {
                const currentHistory = JSON.parse(
                    localStorage.getItem('chat-o-history') || '[]'
                );
                sendMessage(message, currentHistory);
            }
        }, 300);
    }

    /**
     * Handle Enter key in input
     */
    function handleInputKeydown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            
            const message = userInput.value.trim();
            if (!message) return;
            
            const currentHistory = JSON.parse(
                localStorage.getItem('chat-o-history') || '[]'
            );
            
            sendMessage(message, currentHistory);
        }
    }

    /**
     * Auto-resize textarea
     */
    function resizeTextarea() {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    }

    /**
     * Initialize event listeners
     */
    function init() {
        loadHistory();
        
        // Hide empty state if we have history
        if (history.length > 0) {
            hideEmptyState();
        }
        
        // Suggestion chips
        suggestionChips.forEach(chip => {
            chip.addEventListener('click', () => {
                handleSuggestion(chip.dataset.message);
            });
            
            chip.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    handleSuggestion(chip.dataset.message);
                }
            });
        });
        
        // Input handlers
        userInput.addEventListener('input', () => {
            resizeTextarea();
        });
        
        userInput.addEventListener('keydown', handleInputKeydown);
        
        // Send button
        sendBtn.addEventListener('click', () => {
            const message = userInput.value.trim();
            if (!message) return;
            
            const currentHistory = JSON.parse(
                localStorage.getItem('chat-o-history') || '[]'
            );
            
            sendMessage(message, currentHistory);
        });
        
        // Focus input on load
        userInput.focus();
    }

    // Start!
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
