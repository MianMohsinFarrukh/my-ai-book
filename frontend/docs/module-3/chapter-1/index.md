---
title: AI Book Assistant Chatbot
sidebar_position: 1
---

# AI Book Assistant Chatbot

The AI Book Assistant Chatbot provides an interactive way for readers to ask questions about the book content and receive relevant answers. The chatbot is integrated seamlessly into the documentation site with a floating interface that doesn't disrupt the reading experience.

## Features

- **Floating Chat Interface**: Access the chatbot anytime with a floating button in the bottom-right corner
- **Context-Aware Questions**: Select text on any page and ask specific questions about that content
- **Real-time Responses**: Get instant answers from the AI assistant based on book content
- **Mobile Responsive**: Works seamlessly across all device sizes
- **Typing Indicators**: Visual feedback when the AI is processing your request

## How to Use

1. Click the chat icon 💬 in the bottom-right corner of any page
2. Type your question about the book content in the message input
3. Press Enter or click Send to submit your question
4. Receive a relevant response from the AI assistant

### Context-Aware Questions

To ask questions about specific content:

1. Select the text you want to ask about
2. The text selection popup will appear
3. Click "Ask AI" or open the chat and your selected text will be available as context
4. Ask your question related to the selected text

## Integration with CloudCode and SpeckitPlus

The chatbot is built using Stream Chat React components for the UI and integrates with the existing `api.chat` backend service. It's wrapped with `BrowserOnly` to ensure server-side rendering compatibility with Docusaurus.

### Technical Architecture

- **Frontend**: Stream Chat React components
- **Backend**: Integration with existing API service
- **SSR Safety**: Wrapped in Docusaurus `BrowserOnly` component
- **State Management**: React hooks for UI state and text selection
- **Responsive Design**: Mobile-first approach with CSS media queries

## API Integration

The chatbot connects to the backend through the existing API service:

```javascript
api.chat(query, selectedText, contextOverride, sessionId)
```

This allows the chatbot to leverage existing AI processing capabilities while providing a modern chat interface.