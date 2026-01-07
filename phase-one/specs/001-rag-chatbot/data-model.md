# Data Model: Integrated RAG Chatbot for Docusaurus Book

**Date**: 2025-12-16
**Feature**: 001-rag-chatbot
**Related**: [Plan](./plan.md), [Spec](./spec.md), [Research](./research.md)

## Overview

This document defines the data models for the RAG chatbot system, including both relational database schemas and vector database structures. The models are designed to support the functional requirements while maintaining data integrity and performance.

## Relational Database Models (Neon Postgres)

### 1. ChatSession

Represents a user's conversation with the chatbot.

```sql
Table: chat_sessions
- id (UUID, Primary Key, Default: gen_random_uuid())
- user_id (VARCHAR, Optional, for identifying returning users)
- created_at (TIMESTAMPTZ, Default: NOW())
- updated_at (TIMESTAMPTZ, Default: NOW())
- metadata (JSONB, for storing session-specific data)
- is_active (BOOLEAN, Default: true)
```

**Validation Rules**:
- `created_at` must be before `updated_at`
- `user_id` must follow standard identifier format if provided

### 2. ChatMessage

Represents individual messages within a conversation.

```sql
Table: chat_messages
- id (UUID, Primary Key, Default: gen_random_uuid())
- session_id (UUID, Foreign Key: chat_sessions.id)
- role (VARCHAR, Check: 'user' | 'assistant' | 'system')
- content (TEXT, NOT NULL)
- timestamp (TIMESTAMPTZ, Default: NOW())
- context_used (JSONB, for tracking which content was used)
- message_type (VARCHAR, Check: 'query' | 'response' | 'context-only', Default: 'query')
```

**Validation Rules**:
- `session_id` must reference an existing chat session
- `role` must be one of the allowed values
- `content` cannot be empty
- `context_used` should contain references to source content when applicable

### 3. ContentChunk

Represents processed chunks of book content stored in the relational database (metadata only; vectors stored in Qdrant).

```sql
Table: content_chunks
- id (UUID, Primary Key, Default: gen_random_uuid())
- source_file (VARCHAR, NOT NULL, e.g., 'docs/intro.md')
- chunk_index (INTEGER, NOT NULL)
- content (TEXT, NOT NULL)
- embedding_id (VARCHAR, NOT NULL, references Qdrant point ID)
- created_at (TIMESTAMPTZ, Default: NOW())
- metadata (JSONB, for additional content metadata)
- hash (VARCHAR, for detecting content changes)
```

**Validation Rules**:
- `source_file` must follow valid path format
- `chunk_index` must be non-negative
- `embedding_id` must be unique
- `hash` enables change detection

### 4. UserFeedback

Stores user feedback on chat responses to improve quality over time.

```sql
Table: user_feedback
- id (UUID, Primary Key, Default: gen_random_uuid())
- message_id (UUID, Foreign Key: chat_messages.id)
- session_id (UUID, Foreign Key: chat_sessions.id)
- feedback_type (VARCHAR, Check: 'positive' | 'negative' | 'incorrect')
- comment (TEXT, Optional)
- created_at (TIMESTAMPTZ, Default: NOW())
- resolved (BOOLEAN, Default: false)
```

**Validation Rules**:
- Either `message_id` or `session_id` must be provided
- `feedback_type` must be one of the allowed values

## Vector Database Models (Qdrant)

### 1. Content Vector Collection

Qdrant collection schema for storing content embeddings.

**Collection Name**: `book_content`

**Vector Configuration**:
- Size: 1536 (for OpenAI embeddings) or appropriate size for chosen embedding model
- Distance: Cosine similarity

**Payload Structure**:
```json
{
  "content_id": "UUID of the content chunk",
  "source_file": "Source document path",
  "chunk_index": "Index within the source document",
  "metadata": {
    "section": "Document section title",
    "page": "Page number if applicable",
    "tags": ["array", "of", "relevant", "tags"]
  },
  "created_at": "ISO timestamp"
}
```

**Validation Rules**:
- Each payload must have a unique `content_id`
- `source_file` must reference a valid document path
- `chunk_index` must be consistent with document structure

## API Contract Models

### 1. ChatRequest

Model for requests to the chat API.

```json
{
  "query": "string, the user's question",
  "selected_text": "string, optional selected text for context override",
  "session_id": "string, optional session identifier",
  "context_override": "boolean, whether to use selected_text as primary context",
  "options": {
    "temperature": "number, 0.0-1.0",
    "max_tokens": "integer",
    "response_format": "string, 'text' | 'json'"
  }
}
```

**Validation Rules**:
- `query` must be provided and non-empty
- `selected_text` can only be used with `context_override: true`
- `options` values must be within valid ranges

### 2. ChatResponse

Model for responses from the chat API.

```json
{
  "response": "string, the AI-generated response",
  "session_id": "string, session identifier",
  "message_id": "string, unique identifier for this message",
  "context_used": [
    {
      "source": "string, source document",
      "content": "string, relevant content snippet",
      "similarity": "number, 0.0-1.0 similarity score"
    }
  ],
  "grounding_confidence": "number, 0.0-1.0 confidence in response grounding",
  "timestamp": "ISO timestamp"
}
```

**Validation Rules**:
- `response` must be non-empty
- `context_used` should be populated when response is based on book content
- `grounding_confidence` must be between 0.0 and 1.0

### 3. IngestionRequest

Model for content ingestion requests.

```json
{
  "source_path": "string, path to markdown files",
  "chunk_size": "integer, default 1000",
  "overlap": "integer, default 200",
  "metadata": {
    "book_id": "string, identifier for the book",
    "version": "string, book version"
  }
}
```

**Validation Rules**:
- `source_path` must exist and be accessible
- `chunk_size` must be positive
- `overlap` must be less than `chunk_size`

## State Transitions

### ChatSession State Transitions
- `active` → `completed`: When user ends conversation or timeout occurs
- `active` → `archived`: After extended period of inactivity

### Message State Transitions
- `pending` → `processed`: When response is generated
- `processed` → `flagged`: When user provides negative feedback
- `flagged` → `resolved`: When issue is addressed

## Relationships

```
ChatSession (1) ←→ (N) ChatMessage
ChatSession (1) ←→ (N) UserFeedback
ChatMessage (1) ←→ (1) UserFeedback (optional)
ContentChunk (1) ←→ (N) Qdrant Vector Points (via embedding_id)
```

## Indexing Strategy

### Relational Database
- Index on `chat_sessions.user_id` for user lookup
- Index on `chat_messages.session_id` for session queries
- Index on `chat_messages.timestamp` for time-based queries
- Index on `content_chunks.embedding_id` for vector lookup
- Index on `content_chunks.source_file` for content queries

### Vector Database
- Payload index on `source_file` for filtering
- Payload index on `metadata.tags` for tag-based queries
- Vector index optimized for cosine similarity search