import React, { useState, useEffect } from 'react';
import ChatKitProvider from './ChatKitProvider';
import FloatingToggle from './FloatingToggle';

// Simple BrowserOnly-like component
const BrowserOnly = ({ children, fallback }) => {
  if (typeof window === 'undefined') {
    return fallback || null;
  }
  return children();
};

const ChatKitBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedText, setSelectedText] = useState('');

  // Function to get selected text
  useEffect(() => {
    const handleSelection = () => {
      const selected = window.getSelection().toString().trim();
      if (selected) {
        setSelectedText(selected);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <FloatingToggle onClick={toggleChat} />
      {isOpen && (
        <ChatKitProvider
          isOpen={isOpen}
          onClose={() => setIsOpen(false)}
          selectedText={selectedText}
          onSelectedTextChange={setSelectedText}
        />
      )}
    </>
  );
};

// Wrapper to ensure browser-only execution
const ChatKitBotWrapper = () => {
  return (
    <BrowserOnly fallback={<div></div>}>
      {() => <ChatKitBot />}
    </BrowserOnly>
  );
};

export default ChatKitBotWrapper;