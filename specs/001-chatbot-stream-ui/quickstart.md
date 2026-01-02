# Quickstart Guide: AI Book Assistant Chatbot

## Prerequisites
- Node.js 18+ installed
- Docusaurus 3.x project set up
- Access to existing api.chat backend service
- Stream Chat application credentials (for production)

## Installation

1. Install Stream Chat dependencies:
```bash
npm install stream-chat stream-chat-react
```

2. Verify your project has the required dependencies:
```bash
npm list react react-dom @docusaurus/core
```

## Basic Setup

### 1. Create the Chatbot Component
Create a new component at `frontend/src/components/Chatbot/Chatbot.jsx`:

```jsx
import React, { useState } from 'react';
import { Chat, Channel, MessageList, MessageInput } from 'stream-chat-react';
import { StreamChat } from 'stream-chat';

// Initialize Stream Chat client
const client = StreamChat.getInstance('YOUR_API_KEY');

// Your Chatbot component implementation
const Chatbot = ({ visible, onClose }) => {
  // Component implementation
};
```

### 2. Set Up Authentication
For development, use temporary tokens. For production, implement secure token generation on your backend.

### 3. Integrate with Existing API
Override the message sending functionality to use your existing `api.chat` function instead of Stream's default API calls.

### 4. Add to Docusaurus Layout
Wrap the Chatbot component with BrowserOnly in your Docusaurus layout to ensure it only renders on the client side.

## Running Locally

1. Start your Docusaurus development server:
```bash
npm run start
```

2. The chatbot should be accessible via the floating toggle button on any documentation page.

## Testing the Integration

1. Open any documentation page
2. Click the floating chat button to open the interface
3. Type a question about the book content
4. Verify that:
   - The message appears in the chat interface
   - The backend API is called
   - The AI response is displayed properly
   - Typing indicators work correctly

## Text Selection Feature

The text selection context feature is enabled automatically. To test:
1. Select text on any documentation page
2. Initiate a chat query
3. Verify that the selected text is included as context for the AI query

## Mobile Responsiveness

Test the chat interface on various screen sizes:
- Mobile (320px - 768px)
- Tablet (768px - 1024px)
- Desktop (1024px+)

Ensure the floating button and chat window adapt properly to different screen sizes.