# Quickstart Guide: Integrated RAG Chatbot for Docusaurus Book

**Date**: 2025-12-16
**Feature**: 001-rag-chatbot
**Related**: [Plan](./plan.md), [Spec](./spec.md)

## Overview

This guide provides the essential steps to set up and run the RAG chatbot system for your Docusaurus-based book. The system enables users to ask questions about book content and receive accurate, context-aware responses.

## Prerequisites

- Python 3.11+
- Node.js 18+ with npm
- UV package manager (`pip install uv`)
- Access to OpenAI API key
- Qdrant Cloud account (free tier available)
- Neon Postgres account (free tier available)

## Environment Setup

### 1. Clone and Navigate to Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Set Up Backend Environment

```bash
# Navigate to backend directory (create if doesn't exist)
mkdir -p backend
cd backend

# Initialize Python project with UV
uv init
uv add fastapi openai python-dotenv qdrant-client asyncpg pydantic
uv sync
```

### 3. Create Environment Variables File

Create a `.env` file in the backend directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Configuration
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=book_content

# Neon Postgres Configuration
DATABASE_URL=postgresql://username:password@ep-xxxxxxx.us-east-1.aws.neon.tech/dbname?sslmode=require

# Application Settings
APP_ENV=development
LOG_LEVEL=info
MAX_QUERY_LENGTH=1000
MAX_RESPONSE_TOKENS=1000
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-4-turbo
```

## Running the Backend Service

### 1. Start the FastAPI Application

```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Run Database Migrations

```bash
# Using Alembic for database migrations
uv run alembic upgrade head
```

### 3. Ingest Book Content

```bash
# Ingest content from Docusaurus docs directory
uv run python -m src.scripts.ingest --source-path ../frontend/docs --chunk-size 1000
```

## Setting Up the Frontend

### 1. Navigate to Frontend Directory

```bash
cd frontend  # Create if doesn't exist
```

### 2. Initialize Docusaurus Project

```bash
npx create-docusaurus@latest my-website classic
cd my-website
```

### 3. Install Chatbot Component Dependencies

```bash
npm install react-markdown @docusaurus/core
```

### 4. Add Chatbot Component

Create a chatbot component at `src/components/Chatbot/index.js`:

```jsx
import React, { useState, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { colorMode } = useColorMode();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
      });

      const data = await response.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  return (
    <div className={`chatbot-container ${colorMode}`}>
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <strong>{msg.role}: </strong> {msg.content}
          </div>
        ))}
        {isLoading && <div className="message assistant">Thinking...</div>}
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this book..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
```

## API Usage Examples

### 1. Basic Chat Query

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "query": "What are the main concepts in chapter 3?"
  }'
```

### 2. Query with Selected Text Context

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "query": "Explain this concept",
    "selected_text": "The main concept is that AI systems need to be trained on diverse datasets to avoid bias.",
    "context_override": true
  }'
```

### 3. Get Chat History

```bash
curl -X GET http://localhost:8000/v1/chat/sess_abc123/history \
  -H "Authorization: Bearer your-token"
```

## Development Commands

### Backend
```bash
# Run with auto-reload
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .
```

### Frontend
```bash
# Start development server
npm run start

# Build for production
npm run build

# Serve production build locally
npm run serve
```

## Testing the Integration

1. Start both backend and frontend servers
2. Navigate to your Docusaurus site
3. Use the embedded chatbot to ask questions about book content
4. Verify responses are accurate and contextually relevant
5. Test selected text functionality by highlighting text and asking context-specific questions

## Deployment

### Backend Deployment
The backend can be deployed to platforms like Render, Railway, or Fly.io. Ensure environment variables are properly configured.

### Frontend Deployment
Docusaurus sites can be deployed to Vercel, Netlify, or GitHub Pages. The chatbot integration will work with standard Docusaurus deployment processes.