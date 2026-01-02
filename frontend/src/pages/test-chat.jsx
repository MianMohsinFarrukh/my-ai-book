import React from 'react';
import Layout from '@theme/Layout';

export default function TestChatPage() {
  return (
    <Layout title="Test Chat Functionality" description="Test page for chatbot functionality">
      <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
        <h1>Test Chat Functionality</h1>
        <p>
          This page is designed to test the chatbot functionality including text selection and context capture.
          Try selecting some text below and using the "Ask AI" popup that appears.
        </p>

        <div style={{
          padding: '1rem',
          margin: '1rem 0',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          border: '1px solid #ddd'
        }}>
          <h2>Sample Text for Testing</h2>
          <p>
            This is a sample paragraph to test the text selection functionality.
            You can select any part of this text and click the "Ask AI" button that appears to test the context capture.
            The selected text should be sent to the AI assistant as context for your question.
          </p>

          <p>
            Here's another paragraph with different content to test multiple selections.
            Try selecting different parts of the text to see how the context capture works.
            The chatbot should receive the selected text and provide relevant answers.
          </p>

          <h3>More Content</h3>
          <p>
            This section contains additional content for testing purposes.
            You can select text from multiple paragraphs to see how the system handles longer selections.
            The text selection popup should appear above the selected text when you release the mouse button.
          </p>
        </div>

        <div style={{
          padding: '1rem',
          margin: '1rem 0',
          backgroundColor: '#e8f4ff',
          borderRadius: '8px',
          border: '1px solid #b3d9ff'
        }}>
          <h3>Technical Information</h3>
          <p>
            The chatbot integration uses Stream Chat for real-time messaging and includes:
          </p>
          <ul>
            <li>Text selection detection</li>
            <li>Context capture from selected text</li>
            <li>Streaming responses from the AI</li>
            <li>Loading states and error handling</li>
            <li>Responsive design for mobile and desktop</li>
          </ul>
        </div>

        <div style={{
          padding: '1rem',
          margin: '1rem 0',
          backgroundColor: '#f0f8e8',
          borderRadius: '8px',
          border: '1px solid #c8e6c9'
        }}>
          <h3>Testing Instructions</h3>
          <ol>
            <li>Select any text from the paragraphs above</li>
            <li>Wait for the "Ask AI" button to appear above the selected text</li>
            <li>Click the button to send the selected text to the chatbot</li>
            <li>Verify that the chat window opens and shows the context</li>
            <li>Check that the AI provides relevant responses</li>
          </ol>
        </div>
      </div>
    </Layout>
  );
}
