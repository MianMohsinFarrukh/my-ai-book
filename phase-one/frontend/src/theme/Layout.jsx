import React, { useState, Suspense } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import OriginalLayout from '@theme-original/Layout';
import { ChatKitBot } from '../components/ChatKit';

// Error boundary component to catch rendering errors
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error in chatbot components:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return null; // Render nothing if there's an error
    }

    return this.props.children;
  }
}

export default function Layout(props) {
  const [selectedText, setSelectedText] = useState('');
  const [shouldOpenChat, setShouldOpenChat] = useState(false);

  const handleAskQuestion = (text) => {
    setSelectedText(text);
    setShouldOpenChat(true); // This will open the chatbot
  };

  return (
    <>
      <OriginalLayout {...props}>
        {props.children}
      </OriginalLayout>
      <BrowserOnly fallback={null}>
        {() => (
          <ErrorBoundary>
            <Suspense fallback={null}>
              <ChatKitBot selectedTextInitial={selectedText} shouldOpen={shouldOpenChat} onOpenChange={(open) => setShouldOpenChat(open)} />
            </Suspense>
          </ErrorBoundary>
        )}
      </BrowserOnly>
    </>
  );
}
