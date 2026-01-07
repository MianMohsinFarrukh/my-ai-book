# ChatKit Components

This directory contains the ChatKit-based AI assistant implementation for the Physical AI & Humanoid Robotics textbook.

## Components

### ChatKitBot.jsx
Main entry point component that wraps the chat functionality with BrowserOnly to ensure it only runs in the browser environment. This prevents SSR issues with Docusaurus.

### ChatKitProvider.jsx
Core chat component that handles:
- Message history and state management
- Integration with the existing AI backend service
- Text selection context handling
- User interface for sending and receiving messages
- Loading states and error handling

### FloatingToggle.jsx
Floating button component that appears on all pages, allowing users to open/close the chat interface. Positioned in the bottom-right corner for accessibility.

## Integration

The chatbot is integrated using Docusaurus clientModules approach in `frontend/src/clientModules/chatbot.js`. This ensures the chatbot is injected at the app root level and available on all pages without causing SSR issues.

## API Integration

The component integrates with the existing AI backend service through `frontend/src/services/api.js`, specifically using the `api.chat()` method to send queries and receive responses.

## Styling

The UI uses inline styles for a clean, professional appearance without requiring custom CSS files. The design follows Docusaurus color schemes for consistency.

## Features

- Floating toggle button available on all pages
- Text selection context capture
- Real-time chat with AI backend
- Responsive design for mobile and desktop
- Loading states and error handling
- Session-based conversation history