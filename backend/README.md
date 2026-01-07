# Book RAG Chatbot Backend

This is the backend service for the RAG chatbot that answers questions about book content.

## Features

- **RAG (Retrieval Augmented Generation)**: Answers questions based on book content only
- **Text Selection Context**: Prioritizes user-selected text when provided
- **Vector Search**: Uses Qdrant for semantic search in book content
- **Session Management**: Maintains conversation history
- **Content Validation**: Ensures responses are grounded in book content
- **Claude Integration**: Enhanced RAG with Claude AI capabilities
- **Stream Chat Integration**: Real-time chat functionality
- **Book Content Generation**: Automatic module and chapter generation via Claude Code Router

## Architecture

The backend consists of several key components:

- **Database Layer**: Neon Postgres for session and message storage
- **Vector Database**: Qdrant for semantic search in book content
- **LLM Integration**: OpenAI API for response generation
- **API Layer**: FastAPI providing REST endpoints
- **Agent Skills**: Reusable skills for RAG operations
- **Subagents**: Specialized agents for ingestion, retrieval, and validation

## Setup

1. **Install dependencies**:
   ```bash
   cd backend
   uv sync
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run the server**:
   ```bash
   uv run python run_server.py
   ```

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - Main chat endpoint
- `POST /api/v1/ingest` - Content ingestion endpoint
- `GET /api/v1/sessions/{session_id}` - Get session details
- `GET /api/v1/sessions/{session_id}/messages` - Get session messages

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `QDRANT_API_KEY` - Your Qdrant API key (if using cloud)
- `QDRANT_URL` - Qdrant instance URL (if using cloud)
- `DATABASE_URL` - Postgres database connection string
- `NEON_DATABASE_URL` - Neon Postgres connection string

## Development

To run in development mode with auto-reload:

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Agent Skills

The system implements several reusable agent skills:

- `retrieve_context_skill`: Retrieve relevant context from vector database
- `answer_from_context_skill`: Generate answers based on provided context
- `validate_grounding_skill`: Ensure responses are grounded in book content

## Subagents

The system includes specialized subagents:

- `ingestion_subagent`: Handles markdown ingestion and embedding
- `retrieval_subagent`: Performs vector search in Qdrant
- `response_guard_subagent`: Ensures answers are strictly grounded

## Frontend Integration

The backend is designed to work with the Docusaurus frontend, providing:

- A floating chatbot interface
- Text selection popup for context-specific queries
- Session persistence across page loads
- Real-time response streaming

## Content Ingestion

To ingest book content:

1. Place your markdown files in the appropriate directory
2. Call the `/api/v1/ingest` endpoint with the source path
3. The system will chunk, embed, and store the content for retrieval

## Book Generation

The system supports automatic book content generation using Claude Code Router:

1. Configure the Claude Code Router with appropriate templates
2. Use the `/api/v1/generate` endpoint to generate modules and chapters
3. The system will automatically structure content for Docusaurus pages

## Testing

The system includes comprehensive error handling and validation to ensure:

- No hallucinations (responses strictly based on book content)
- Proper fallback responses when content is unavailable
- Context-specific answers when user selects text
- Grounding validation to maintain accuracy