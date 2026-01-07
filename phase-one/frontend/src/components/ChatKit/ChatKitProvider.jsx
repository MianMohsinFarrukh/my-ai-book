import React, { useState, useRef, useEffect } from 'react';
import api from '../../services/api';
import './chatkit-styles.css';

const ChatKitProvider = ({ isOpen, onClose, selectedText, onSelectedTextChange }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Add initial welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          content: 'Hello! I\'m your AI assistant for the Physical AI & Humanoid Robotics textbook. How can I help you today?',
          sender: 'ai',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [messages.length]);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    onSelectedTextChange(''); // Clear selected text after sending

    try {
      // Call the existing AI backend service
      const response = await api.chat(inputValue, selectedText || null);

      // Add AI response
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        content: response.response || response.answer || response.content || 'No response received',
        sender: 'ai',
        timestamp: new Date().toISOString(),
        sources: response.sources || response.references || []
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      // Add error message
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'ai',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="chatkit-container">
      <div className="chatkit-header">
        <h3>AI Assistant</h3>
        <button
          className="chatkit-close-button"
          onClick={onClose}
          aria-label="Close chat"
        >
          ×
        </button>
      </div>

      <div className="chatkit-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chatkit-message chatkit-message-${message.sender}`}
          >
            <div className={`chatkit-message-bubble chatkit-message-bubble-${message.sender}`}>
              <div className="chatkit-message-content">
                {message.content}
              </div>
              {message.sources && message.sources.length > 0 && (
                <div className="chatkit-sources">
                  Sources: {message.sources.join(', ')}
                </div>
              )}
              <div className="chatkit-message-timestamp">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="chatkit-message chatkit-message-ai">
            <div className="chatkit-message-bubble chatkit-message-bubble-ai">
              <div>Thinking...</div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="chatkit-input-form">
        {selectedText && (
          <div className="chatkit-selected-text-context">
            Context: "{selectedText.substring(0, 50)}{selectedText.length > 50 ? '...' : ''}"
          </div>
        )}
        <div className="chatkit-input-container">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about the book content..."
            className="chatkit-input"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="chatkit-send-button"
            disabled={!inputValue.trim() || isLoading}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatKitProvider;