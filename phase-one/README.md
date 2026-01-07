# AI Book with RAG Chatbot

This project implements an AI-powered chatbot integrated into a Docusaurus-based book website. The chatbot answers questions based strictly on book content using Retrieval Augmented Generation (RAG).

## Features

- **AI Chatbot**: Answers questions based only on book content
- **Text Selection Context**: Ask questions about selected text with higher priority
- **Session Management**: Maintains conversation history
- **Content Validation**: Ensures no hallucinations - responses grounded in book content
- **Docusaurus Integration**: Seamless integration with existing Docusaurus site

## Architecture

The system consists of:

- **Backend**: FastAPI server with OpenAI integration, Qdrant vector database, and Neon Postgres
- **Frontend**: Docusaurus site with integrated chatbot component
- **Agent Skills**: Reusable skills for RAG operations
- **Subagents**: Specialized agents for ingestion, retrieval, and validation

## Prerequisites

- Python 3.11+
- Node.js 18+
- UV package manager
- Docker (for local Qdrant, optional)

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies using UV:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. Run the backend server:
   ```bash
   uv run python run_server.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the Docusaurus development server:
   ```bash
   npm start
   ```

## Configuration

### Backend Configuration

The backend requires the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_API_KEY`: Your Qdrant API key (if using cloud)
- `QDRANT_URL`: Qdrant instance URL (if using cloud)
- `QDRANT_HOST` and `QDRANT_PORT`: For local Qdrant (defaults: localhost:6333)
- `DATABASE_URL`: Postgres database connection string
- `NEON_DATABASE_URL`: Neon Postgres connection string

### Frontend Configuration

The frontend will connect to the backend at `http://localhost:8000` by default. You can override this by setting the `REACT_APP_API_URL` environment variable.

## Usage

1. Start the backend server (port 8000)
2. Start the frontend development server (port 3000)
3. Navigate to your Docusaurus site
4. Use the chatbot button to open the AI assistant
5. Ask questions about the book content
6. Select text and use the "Ask AI" popup for context-specific questions

## Content Ingestion

To add book content to the chatbot:

1. Place your markdown files in the appropriate directory
2. Call the `/api/v1/ingest` endpoint with the source path
3. The system will chunk, embed, and store the content for retrieval

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

## Development

### Backend Development

The backend is built with FastAPI and includes:

- Async database operations with SQLAlchemy
- Vector search with Qdrant
- OpenAI integration for response generation
- Comprehensive error handling and logging

### Frontend Development

The frontend extends the Docusaurus site with:

- A floating chatbot component
- Text selection popup for context-specific queries
- Session management across page loads
- Real-time response streaming

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - Main chat endpoint
- `POST /api/v1/ingest` - Content ingestion endpoint
- `GET /api/v1/sessions/{session_id}` - Get session details
- `GET /api/v1/sessions/{session_id}/messages` - Get session messages

## Security

- API keys are loaded from environment variables
- Input validation on all endpoints
- Content validation to prevent hallucinations
- Proper CORS configuration

## Testing

The system includes comprehensive validation to ensure:

- No hallucinations (responses strictly based on book content)
- Proper fallback responses when content is unavailable
- Context-specific answers when user selects text
- Grounding validation to maintain accuracy

## Deployment

For production deployment:

1. Set up secure environment variables
2. Configure proper database connections
3. Set up SSL certificates
4. Configure reverse proxy (nginx, etc.)
5. Set up monitoring and logging

## Troubleshooting

If the chatbot doesn't appear on the site:
- Check that the Layout wrapper is properly placed in `frontend/src/theme/Layout.jsx`
- Verify that the backend server is running
- Check browser console for errors

If API calls fail:
- Verify backend server is accessible
- Check environment variables are properly set
- Ensure CORS configuration allows frontend requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.