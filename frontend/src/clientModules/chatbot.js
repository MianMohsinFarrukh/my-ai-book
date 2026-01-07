// Docusaurus client module to inject AI Book Assistant chatbot at app root level
// This ensures the chatbot is available on all pages without SSR issues

import React from 'react';
import { createRoot } from 'react-dom/client';
import ChatKitBot from '../components/ChatKit/ChatKitBot';

// Create a container for the chatbot
const createChatbotContainer = () => {
  let container = document.getElementById('chatbot-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'chatbot-container';
    document.body.appendChild(container);
  }
  return container;
};

// Initialize the chatbot when the DOM is ready
let root;
const initChatbot = () => {
  if (typeof window !== 'undefined' && typeof document !== 'undefined') {
    const container = createChatbotContainer();
    root = createRoot(container);
    root.render(<ChatKitBot />);
  }
};

// Wait for the DOM to be ready before initializing
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
  } else {
    initChatbot();
  }
}

// Export an empty default export since this is a client module
// that runs side effects rather than providing a component
export default {};